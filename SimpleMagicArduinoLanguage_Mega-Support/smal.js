var katescript = {
	"name": "SMAL",
	"author": "David",
	"license": "MIT",
	"revision": 1,
	"kate-version": "5.1",
	"required-syntax-style": "SMAL",
	"indent-languages": ["SMAL"],
	"priority": 10
}; // kate-script-header, must be at the start of the file without comments

function indent(line, indentWidth, ch)
{
	var previousLine = line - 1;

	while (previousLine >= 0 && document.line(previousLine).trim() === "")
		previousLine--;

	if (previousLine < 0)
		return 0;

	var previousText = document.line(previousLine);
	var currentText = document.line(line);

	var previousIndent = previousText.search(/\S|$/);
	var currentIndent = currentText.search(/\S|$/);

	// Nur event, if, while und for erhöhen die Einrückung.
	if (/^(event|if|while|for)\b/.test(previousText.trim()))
		return previousIndent + indentWidth;

	// Bei allen anderen Zeilen bleibt die bisherige Einrückung erhalten.
	if (currentIndent === 0)
		return previousIndent;

	return -1;
}
