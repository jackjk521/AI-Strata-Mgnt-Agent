# app.py - Flask application with Google OR-Tools for print optimization
from flask import Flask, request, jsonify, render_template
from ortools.linear_solver import pywraplp
import math

app = Flask(__name__)

def optimize_printing(client_size, material_size, gutter, bleed, pull, machine_max_length, grain_direction, layout_orientation):
    """
    Optimize printing layout using Google OR-Tools
    
    Parameters:
    - client_size: tuple (length, width) - final required print size
    - material_size: tuple (length, width) - available paper size
    - gutter: float - spacing between printed items
    - bleed: float - extra area for cutting accuracy
    - pull: float - space for machine handling
    - machine_max_length: float - maximum length that can be fed into machine
    - grain_direction: str - 'any', 'lengthwise', or 'widthwise'
    - layout_orientation: str - 'landscape', 'portrait', or 'flexible'
    
    Returns:
    - Dictionary with optimization results
    """
    client_length, client_width = client_size
    material_length, material_width = material_size
    
    # Calculate effective dimensions (including gutter and bleed)
    effective_length = client_length + (2 * bleed) + gutter
    effective_width = client_width + (2 * bleed) + gutter
    
    # Initialize results
    all_configurations = []
    
    # Determine which orientations to check
    client_orientations = []
    if layout_orientation == 'flexible':
        client_orientations = ['portrait', 'landscape']
    else:
        client_orientations = [layout_orientation]
    
    # Check both material orientations
    material_orientations = [
        {"name": "Standard", "length": material_length, "width": material_width},
        {"name": "Rotated", "length": material_width, "width": material_length}
    ]
    
    # Filter out material orientations that exceed machine constraints
    valid_material_orientations = [
        m for m in material_orientations 
        if m["width"] <= machine_max_length
    ]
    
    # Process all valid combinations
    for client_orientation in client_orientations:
        # Determine client piece dimensions based on orientation
        if client_orientation == 'landscape':
            piece_length = max(effective_length, effective_width)
            piece_width = min(effective_length, effective_width)
        else:  # portrait
            piece_length = min(effective_length, effective_width)
            piece_width = max(effective_length, effective_width)
        
        for material_option in valid_material_orientations:
            mat_length = material_option["length"]
            mat_width = material_option["width"]
            
            # Skip if grain direction constraints are not met
            if grain_direction == 'lengthwise' and material_option["name"] == "Rotated":
                continue
            if grain_direction == 'widthwise' and material_option["name"] == "Standard":
                continue
            
            # Calculate using math (simpler than OR-Tools for this specific problem)
            # How many pieces can fit in each direction
            pieces_along_length = math.floor((mat_length - pull) / piece_length)
            pieces_along_width = math.floor((mat_width - pull) / piece_width)
            
            # Calculate total pieces on this sheet
            total_pieces = pieces_along_length * pieces_along_width
            
            if total_pieces > 0:
                # Calculate standard sheet outs (8.5 x 11)
                standard_length = 8.5
                standard_width = 11
                
                # Check both orientations for standard size cuts
                std_pieces_option1 = math.floor(mat_length / standard_length) * math.floor(mat_width / standard_width)
                std_pieces_option2 = math.floor(mat_length / standard_width) * math.floor(mat_width / standard_length)
                
                standard_sheet_outs = max(std_pieces_option1, std_pieces_option2)
                
                # Calculate the efficiency
                efficiency = (total_pieces * piece_length * piece_width) / (mat_length * mat_width) * 100
                
                # Store the configuration
                config = {
                    "materialOrientation": material_option["name"],
                    "clientOrientation": client_orientation,
                    "printingSize": {"length": 8.5, "width": 11},  # Standard size
                    "actualPrintingSize": {"length": piece_length, "width": piece_width},
                    "piecesAlongLength": pieces_along_length,
                    "piecesAlongWidth": pieces_along_width,
                    "printingOuts": total_pieces,
                    "standardSizeOuts": standard_sheet_outs,
                    "totalOuts": total_pieces * standard_sheet_outs,
                    "efficiency": efficiency
                }
                
                all_configurations.append(config)
    
    # Sort configurations by total outs (descending)
    all_configurations.sort(key=lambda x: x["totalOuts"], reverse=True)
    
    # If no valid configuration was found
    if not all_configurations:
        return {
            "printingSize": {"length": 0, "width": 0},
            "printingOuts": 0,
            "standardSizeOuts": 0,
            "totalOuts": 0,
            "configurations": [],
            "bestConfig": None
        }
    
    # Get the best configuration
    best_config = all_configurations[0]
    
    return {
        "printingSize": {"length": 8.5, "width": 11},  # Standard size
        "printingOuts": best_config["printingOuts"],
        "standardSizeOuts": best_config["standardSizeOuts"],
        "totalOuts": best_config["totalOuts"],
        "configurations": all_configurations,
        "bestConfig": best_config
    }


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/optimize', methods=['POST'])
def optimize():
    data = request.json
    
    # Extract input parameters
    client_size = (float(data['clientLength']), float(data['clientWidth']))
    material_size = (float(data['materialLength']), float(data['materialWidth']))
    gutter = float(data['gutter'])
    bleed = float(data['bleed'])
    pull = float(data['pull'])
    machine_max_length = float(data['machineMaxLength'])
    grain_direction = data['grainDirection']
    layout_orientation = data['orientation']
    
    # Call optimization function
    results = optimize_printing(
        client_size, 
        material_size,
        gutter,
        bleed,
        pull,
        machine_max_length,
        grain_direction,
        layout_orientation
    )
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 