from docxtpl import DocxTemplate
import json

tpl = DocxTemplate("src/templates/validation_template20250916.docx")
ctx = json.load(open("context_docxtpl_validacion.json", "r", encoding="utf-8"))
tpl.render(ctx)
tpl.save("reporte_validacion_renderizado.docx")
