import io
import csv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, date

from ..database import get_db
from .. import models
from ..auth import require_technicien, require_authentifie

router = APIRouter(prefix="/statistiques", tags=["Statistiques"])


# ---------- Résumé global ----------
@router.get("/resume")
def stats_resume(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    total_equipements = db.query(models.Equipement).filter(
        models.Equipement.actif == True
    ).count()

    total_interventions = db.query(models.Intervention).filter(
        models.Intervention.archive == False
    ).count()

    en_attente = db.query(models.Intervention).filter(
        models.Intervention.statut == "en_attente",
        models.Intervention.archive == False
    ).count()

    en_cours = db.query(models.Intervention).filter(
        models.Intervention.statut == "en_cours",
        models.Intervention.archive == False
    ).count()

    terminees = db.query(models.Intervention).filter(
        models.Intervention.statut == "terminee",
        models.Intervention.archive == False
    ).count()

    equipements_disponibles = db.query(models.Equipement).filter(
        models.Equipement.actif == True,
        models.Equipement.statut == "disponible"
    ).count()

    equipements_occupes = db.query(models.Equipement).filter(
        models.Equipement.actif == True,
        models.Equipement.statut == "occupé"
    ).count()

    return {
        "total_equipements": total_equipements,
        "total_interventions": total_interventions,
        "en_attente": en_attente,
        "en_cours": en_cours,
        "terminees": terminees,
        "equipements_disponibles": equipements_disponibles,
        "equipements_occupes": equipements_occupes,
    }


# ---------- Interventions par statut ----------
@router.get("/par-statut")
def stats_par_statut(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    resultats = db.query(
        models.Intervention.statut,
        func.count(models.Intervention.id).label("total")
    ).filter(
        models.Intervention.archive == False
    ).group_by(models.Intervention.statut).all()

    return [{"statut": r[0], "total": r[1]} for r in resultats]


# ---------- Pannes par mois ----------
@router.get("/par-mois")
def stats_par_mois(
    annee: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    query = db.query(
        func.strftime("%Y-%m", models.Intervention.date_signalement).label("mois"),
        func.count(models.Intervention.id).label("total")
    ).filter(models.Intervention.archive == False)

    if annee:
        query = query.filter(
            func.strftime("%Y", models.Intervention.date_signalement) == str(annee)
        )

    resultats = query.group_by("mois").order_by("mois").all()
    return [{"mois": r[0], "total": r[1]} for r in resultats]


# ---------- Pannes par priorité ----------
@router.get("/par-priorite")
def stats_par_priorite(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    resultats = db.query(
        models.Priorite.nom,
        models.Priorite.couleur,
        func.count(models.Intervention.id).label("total")
    ).join(
        models.Intervention,
        models.Intervention.priorite_id == models.Priorite.id
    ).filter(
        models.Intervention.archive == False
    ).group_by(models.Priorite.id).all()

    return [{"priorite": r[0], "couleur": r[1], "total": r[2]} for r in resultats]


# ---------- Top équipements en panne ----------
@router.get("/equipements-en-panne")
def stats_equipements_panne(
    limite: int = 10,
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    resultats = db.query(
        models.Equipement.id,
        models.Equipement.marque,
        models.Equipement.modele,
        models.Equipement.numero_serie,
        models.TypeEquipement.nom.label("type_nom"),
        func.count(models.Intervention.id).label("nombre_pannes")
    ).join(
        models.Intervention,
        models.Intervention.equipement_id == models.Equipement.id
    ).join(
        models.TypeEquipement,
        models.Equipement.type_id == models.TypeEquipement.id
    ).filter(
        models.Intervention.archive == False
    ).group_by(models.Equipement.id).order_by(
        func.count(models.Intervention.id).desc()
    ).limit(limite).all()

    return [
        {
            "equipement_id": r[0],
            "marque": r[1],
            "modele": r[2],
            "numero_serie": r[3],
            "type": r[4],
            "nombre_pannes": r[5]
        }
        for r in resultats
    ]


# ---------- Pannes par service ----------
@router.get("/par-service")
def stats_par_service(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    resultats = db.query(
        models.Service.nom,
        func.count(models.Intervention.id).label("total")
    ).join(
        models.Utilisateur,
        models.Utilisateur.service_id == models.Service.id
    ).join(
        models.Intervention,
        models.Intervention.utilisateur_id == models.Utilisateur.id
    ).filter(
        models.Intervention.archive == False
    ).group_by(models.Service.id).all()

    return [{"service": r[0], "total": r[1]} for r in resultats]


# ---------- Temps moyens ----------
@router.get("/temps-moyens")
def stats_temps_moyens(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    interventions = db.query(models.Intervention).filter(
        models.Intervention.date_prise_en_charge.isnot(None),
        models.Intervention.archive == False
    ).all()

    if not interventions:
        return {
            "temps_moyen_prise_en_charge_heures": 0,
            "temps_moyen_resolution_heures": 0,
            "nombre_interventions_analysees": 0
        }

    total_prise = 0
    total_resolution = 0
    nb_prise = 0
    nb_resolution = 0

    for i in interventions:
        if i.date_prise_en_charge and i.date_signalement:
            delta = (i.date_prise_en_charge - i.date_signalement).total_seconds() / 3600
            total_prise += delta
            nb_prise += 1
        if i.date_fin and i.date_prise_en_charge:
            delta = (i.date_fin - i.date_prise_en_charge).total_seconds() / 3600
            total_resolution += delta
            nb_resolution += 1

    return {
        "temps_moyen_prise_en_charge_heures": round(total_prise / nb_prise, 2) if nb_prise else 0,
        "temps_moyen_resolution_heures": round(total_resolution / nb_resolution, 2) if nb_resolution else 0,
        "nombre_interventions_analysees": len(interventions)
    }


# ---------- Export CSV ----------
@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    interventions = db.query(models.Intervention).filter(
        models.Intervention.archive == False
    ).order_by(models.Intervention.date_signalement.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        "ID", "Date signalement", "Date prise en charge", "Date fin",
        "Employe", "Equipement", "Priorite", "Statut",
        "Description", "Actions realisees", "Resultat"
    ])

    for i in interventions:
        writer.writerow([
            i.id,
            i.date_signalement.strftime("%Y-%m-%d %H:%M") if i.date_signalement else "",
            i.date_prise_en_charge.strftime("%Y-%m-%d %H:%M") if i.date_prise_en_charge else "",
            i.date_fin.strftime("%Y-%m-%d %H:%M") if i.date_fin else "",
            i.utilisateur.nom if i.utilisateur else "",
            f"{i.equipement.marque} {i.equipement.modele or ''} ({i.equipement.numero_serie})" if i.equipement else "",
            i.priorite.nom if i.priorite else "",
            i.statut,
            i.description_panne,
            i.actions_realisees or "",
            i.resultat or ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=interventions_{date.today()}.csv"
        }
    )


# ---------- Export PDF ----------
@router.get("/export/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    _: models.Utilisateur = Depends(require_technicien)
):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import cm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1*cm, rightMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )

    styles = getSampleStyleSheet()
    titre_style = ParagraphStyle(
        'Titre',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor("#1a237e"),
        spaceAfter=10
    )

    elements = []
    elements.append(Paragraph("LIMA GROUP - Rapport de Maintenance Informatique", titre_style))
    elements.append(Paragraph(f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    total = db.query(models.Intervention).filter(models.Intervention.archive == False).count()
    terminees = db.query(models.Intervention).filter(
        models.Intervention.statut == "terminee",
        models.Intervention.archive == False
    ).count()
    en_cours = db.query(models.Intervention).filter(
        models.Intervention.statut == "en_cours",
        models.Intervention.archive == False
    ).count()
    en_attente = db.query(models.Intervention).filter(
        models.Intervention.statut == "en_attente",
        models.Intervention.archive == False
    ).count()

    elements.append(Paragraph("Resume", styles['Heading2']))
    resume_data = [
        ["Total interventions", "Terminees", "En cours", "En attente"],
        [str(total), str(terminees), str(en_cours), str(en_attente)]
    ]
    resume_table = Table(resume_data, colWidths=[6*cm]*4)
    resume_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(resume_table)
    elements.append(Spacer(1, 1*cm))

    elements.append(Paragraph("Detail des interventions", styles['Heading2']))

    data = [["ID", "Date", "Employe", "Equipement", "Priorite", "Statut", "Description"]]
    interventions = db.query(models.Intervention).filter(
        models.Intervention.archive == False
    ).order_by(models.Intervention.date_signalement.desc()).limit(100).all()

    for i in interventions:
        data.append([
            str(i.id),
            i.date_signalement.strftime("%d/%m/%Y") if i.date_signalement else "",
            i.utilisateur.nom if i.utilisateur else "",
            f"{i.equipement.marque} ({i.equipement.numero_serie})" if i.equipement else "",
            i.priorite.nom if i.priorite else "",
            i.statut,
            (i.description_panne[:50] + "...") if len(i.description_panne) > 50 else i.description_panne
        ])

    table = Table(data, colWidths=[1*cm, 2*cm, 3*cm, 4*cm, 2*cm, 2.5*cm, 11*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rapport_maintenance_{date.today()}.pdf"
        }
    )
