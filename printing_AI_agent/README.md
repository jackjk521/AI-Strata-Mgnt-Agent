# Printing Optimization Tool with Flask and Google OR-Tools

This application optimizes printing layouts to maximize efficiency and minimize waste, using Google OR-Tools for powerful mathematical optimization.

## Requirements

```
Flask==2.3.3
ortools==9.7.2996
```

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install Flask==2.3.3 ortools==9.7.2996
```

3. Create the directory structure:
```
print-optimizer/
├── app.py
└── templates/
    └── index.html
```

4. Copy the provided code files to their respective locations.

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

## How It Works

The application uses Google OR-Tools' linear solver to find the optimal arrangement of printed items on a sheet of material, considering:

1. Client size dimensions
2. Material size constraints
3. Printing requirements (gutter, bleed, pull)
4. Machine limitations
5. Orientation preferences

The optimization process:
- Considers all valid orientations of both the client piece and material sheet
- Calculates the maximum number of pieces that can fit while respecting constraints
- Determines how many standard-sized sheets (8.5 × 11) can be produced
- Calculates total output and material efficiency
- Ranks configurations by total output

## Features

- Interactive web interface
- Real-time calculations
- Visual representation of the optimized layout
- Detailed configuration information
- Alternative layout suggestions