const vscode = require('vscode');
const fs     = require('fs');
const path   = require('path');

function getWebviewContent(context, panel) {
	const webviewPath = path.join(context.extensionPath, 'src', 'webview');

	const htmlPath = path.join(webviewPath, 'index.html');
	const cssPath = path.join(webviewPath, 'style.css');
	const jsPath = path.join(webviewPath, 'main.js');

	const htmlContent = fs.readFileSync(htmlPath, 'utf8');
	const cssUri = panel.webview.asWebviewUri(vscode.Uri.file(cssPath));
	const jsUri = panel.webview.asWebviewUri(vscode.Uri.file(jsPath));

	return htmlContent
		.replace('{{styleUri}}', cssUri.toString())
		.replace('{{scriptUri}}', jsUri.toString());
}

module.exports = {
	getWebviewContent
}
