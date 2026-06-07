import json
import os
import subprocess
import tempfile


def bicep_to_json(bicep_input):
    """
    Convert Bicep to ARM template JSON using 'bicep build' command.
    Note: This function requires the Bicep CLI to be installed and available in the system PATH.
    """
    
    # Write Bicep content to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.bicep') as temp_bicep:
        temp_bicep.write(bicep_input)
        temp_bicep_path = temp_bicep.name
    
    # Output JSON will be in same directory with same name but .json extension
    json_output_path = temp_bicep_path.replace('.bicep', '.json')
    
    try:
        # Run bicep build command
        result = subprocess.run(
            ['bicep', 'build', temp_bicep_path, '--outfile', json_output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Bicep build failed: {result.stderr}")
        
        # Read and return the generated JSON
        with open(json_output_path, 'r') as f:
            return json.load(f)
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_bicep_path):
            os.remove(temp_bicep_path)
