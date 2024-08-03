"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = __importStar(require("vscode"));
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Extension "knowledgeiskey" is now active!');
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    const disposable = vscode.commands.registerCommand('knowledgeiskey.addCodeMarker', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        let activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            return;
        }
        const selection = activeEditor.selection;
        const { exec } = require('child_process');
        // call main app to get the urr subsection and imIdx
        exec(__dirname + '/mainAppCall.sh ' + activeEditor.document.fileName + " add", (err, stdout, stderr) => {
            if (stdout !== "None\n") {
                let languageId = activeEditor.document.languageId;
                let markerText = stdout.replace(/(\r\n|\n|\r)/gm, "");
                let markerPrefix = (languageId === "python") ? "\n#" : "\n//";
                markerText = markerPrefix + markerText;
                // insert a marker
                activeEditor.edit((selectedText) => {
                    selectedText.replace(activeEditor.selection, markerText);
                });
                activeEditor.document.save();
            }
            else {
                vscode.window.showInformationMessage("No marker added!");
            }
        });
    });
    context.subscriptions.push(disposable);
    const disposable2 = vscode.commands.registerCommand('knowledgeiskey.deleteCodeMarker', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        let activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor) {
            return;
        }
        const selection = activeEditor?.selection;
        const { exec } = require('child_process');
        // call main app to get the urr subsection and imIdx
        exec(__dirname + '/mainAppCall.sh ' + activeEditor.document.fileName + ' delete', (err, stdout, stderr) => {
            if (stdout !== '') {
                let languageId = activeEditor.document.languageId;
                let markerText = stdout.replace(/(\r\n|\n|\r)/gm, "");
                let markerPrefix = (languageId === "python") ? "\n#" : "\n//";
                markerText = markerPrefix + markerText;
                let fullText = activeEditor.document.getText();
                let textReplace = fullText.replace(markerText, ``);
                vscode.window.showInformationMessage(textReplace);
                let invalidRange = new vscode.Range(0, 0, activeEditor.document.lineCount, 0);
                let validFullRange = activeEditor.document.validateRange(invalidRange);
                activeEditor.edit(editBuilder => {
                    editBuilder.replace(validFullRange, textReplace);
                });
                activeEditor.document.save();
            }
        });
    });
    context.subscriptions.push(disposable2);
}
// This method is called when your extension is deactivated
function deactivate() { }
//# sourceMappingURL=extension.js.map