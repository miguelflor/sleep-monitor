# Sleep Monitor - Project Report

This directory contains the LaTeX source files for the IoT & Mobile Systems (2025/26) project report.

## Project Structure

```
report/
├── main.tex                    # Main LaTeX document
├── sections/                   # Individual section files
│   ├── 01_introduction.tex
│   ├── 02_general_overview.tex
│   ├── 03_system_architecture.tex
│   ├── 04_mobile_application.tex
│   ├── 05_sensing_and_reacting.tex
│   ├── 06_experiments.tex
│   └── 07_conclusions.tex
├── images/                     # Directory for images and diagrams
└── README.md                   # This file
```

## How to Compile

### Using pdflatex
```bash
pdflatex main.tex
pdflatex main.tex  # Run twice for proper references
```

### Using latexmk (recommended)
```bash
latexmk -pdf main.tex
```

### Clean build files
```bash
latexmk -c  # Clean auxiliary files
latexmk -C  # Clean all generated files including PDF
```

## Requirements

The template uses the following LaTeX packages:
- inputenc
- babel
- graphicx
- hyperref
- geometry
- listings
- xcolor
- fancyhdr
- titlesec
- float
- subcaption

Make sure you have a complete LaTeX distribution installed (e.g., TeX Live, MiKTeX).

## Customization

### Title Page
Edit the title page section in `main.tex` to add:
- Your names and student numbers
- Correct project title (currently "Sleep Monitor")

### Images
Place all images, diagrams, and screenshots in the `images/` directory and reference them using:
```latex
\includegraphics[width=0.8\textwidth]{images/your_image.png}
```

### Code Listings
Use the `lstlisting` environment for code:
```latex
\begin{lstlisting}[language=Python, caption={Your Caption}]
# Your code here
\end{lstlisting}
```

## Section Guidelines

Each section file contains TODO comments and structure based on the project requirements. Fill in the content following the guidelines provided in each file.

## Tips

1. Run pdflatex twice to ensure all references are correct
2. Use `\label{}` and `\ref{}` for cross-references
3. Place images in the `images/` directory
4. Keep each section in its separate file for better organization
5. Comment out unused subsections if needed
