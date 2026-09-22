import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/workspace/scratch/2ebcebc799d2/cbt_assessment_system/sample_files";
const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Questions");
sheet.showGridLines = false;
sheet.getRange("A1:G5").values = [
  ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer", "Mark"],
  ["Python is best described as a:", "Programming language", "Database server", "Web browser", "Spreadsheet", "A", 1],
  ["Which keyword defines a function in Python?", "func", "define", "def", "function", "C", 1],
  ["What does CPU stand for?", "Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Control Processing User", "A", 1],
  ["Which data type stores True or False?", "String", "Boolean", "Integer", "List", "B", 1],
];
sheet.getRange("A1:G1").format = {
  fill: "#174F3F",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange("A2:G200").format.font = { name: "Arial", size: 10, color: "#13221E" };
sheet.getRange("A2:G200").format.verticalAlignment = "center";
sheet.getRange("A2:F200").format.wrapText = true;
sheet.getRange("A1:G200").format.borders = { preset: "inside", style: "thin", color: "#DCE3DF" };
sheet.getRange("A2:G5").format.fill = "#F8FAF9";
sheet.getRange("A1:A200").format.columnWidth = 42;
sheet.getRange("B1:E200").format.columnWidth = 25;
sheet.getRange("F1:F200").format.columnWidth = 18;
sheet.getRange("G1:G200").format.columnWidth = 10;
sheet.getRange("A1:G1").format.rowHeight = 32;
sheet.getRange("A2:G5").format.rowHeight = 44;
sheet.freezePanes.freezeRows(1);
sheet.getRange("F2:F200").dataValidation = { rule: { type: "list", values: ["A", "B", "C", "D"] } };
sheet.getRange("G2:G200").dataValidation = { rule: { type: "whole", operator: "between", formula1: 1, formula2: 100 } };
workbook.recalculate();
const inspect = await workbook.inspect({kind:"table", range:"Questions!A1:G5", include:"values,formulas", tableMaxRows:6, tableMaxCols:7});
console.log(inspect.ndjson);
const errors = await workbook.inspect({kind:"match", searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options:{useRegex:true,maxResults:50}, summary:"final formula error scan"});
console.log(errors.ndjson);
await fs.mkdir(outputDir, {recursive:true});
const preview = await workbook.render({sheetName:"Questions", range:"A1:G8", scale:1.4, format:"png"});
await fs.writeFile(`${outputDir}/CBT_Question_Upload_Template_preview.png`, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/CBT_Question_Upload_Template.xlsx`);
