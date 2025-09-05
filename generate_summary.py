#!/usr/bin/env python3
"""
Generate HTML summary report from markdown
"""

def markdown_to_html(md_file, html_file):
    """Convert markdown to styled HTML"""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple markdown to HTML conversion
    html_content = content.replace('\n\n', '\n<p></p>\n')
    
    # Convert headers
    html_content = html_content.replace('### ', '<h3>').replace('\n<h3>', '\n<h3>').replace('</h3>', '</h3>')
    html_content = html_content.replace('## ', '<h2>').replace('\n<h2>', '\n<h2>').replace('</h2>', '</h2>')
    html_content = html_content.replace('# ', '<h1>').replace('\n<h1>', '\n<h1>').replace('</h1>', '</h1>')
    
    # Convert code blocks
    lines = html_content.split('\n')
    in_code_block = False
    processed_lines = []
    
    for line in lines:
        if line.startswith('```'):
            if in_code_block:
                processed_lines.append('</pre>')
                in_code_block = False
            else:
                processed_lines.append('<pre>')
                in_code_block = True
        else:
            if line.startswith('- '):
                line = '<li>' + line[2:] + '</li>'
            elif line.startswith('* '):
                line = '<li>' + line[2:] + '</li>'
            elif line.startswith('#### '):
                line = '<h4>' + line[5:] + '</h4>'
            
            processed_lines.append(line)
    
    html_content = '\n'.join(processed_lines)
    
    # CSS styling
    css = """
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            margin: 40px auto; 
            max-width: 1000px;
            color: #333;
            background-color: #f9f9f9;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 15px; 
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        h2 { 
            color: #34495e; 
            border-bottom: 2px solid #bdc3c7; 
            margin-top: 40px; 
            padding-bottom: 10px;
            font-size: 1.8em;
        }
        h3 { 
            color: #7f8c8d; 
            margin-top: 25px;
            font-size: 1.4em;
        }
        h4 {
            color: #95a5a6;
            margin-top: 20px;
            font-size: 1.2em;
        }
        pre { 
            background-color: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            overflow-x: auto;
            border-left: 4px solid #3498db;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
        }
        li {
            margin: 8px 0;
            list-style-type: none;
            padding-left: 20px;
            position: relative;
        }
        li:before {
            content: "•";
            color: #3498db;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        .highlight {
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
            border-radius: 5px;
        }
        .status-complete { color: #27ae60; font-weight: bold; }
        .status-next { color: #e74c3c; font-weight: bold; }
        .emoji { font-size: 1.2em; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .section {
            margin: 30px 0;
            padding: 20px 0;
        }
    </style>
    """
    
    # Full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blackjack ML System Development Summary</title>
        {css}
    </head>
    <body>
        <div class="container">
            {html_content}
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ HTML summary generated: {html_file}")
    print("📄 To convert to PDF:")
    print("   1. Open the HTML file in your browser")
    print("   2. Use 'Print' -> 'Save as PDF'")
    print("   3. Or use online HTML to PDF converters")

if __name__ == "__main__":
    markdown_to_html('project_summary.md', 'Blackjack_ML_System_Summary.html')
