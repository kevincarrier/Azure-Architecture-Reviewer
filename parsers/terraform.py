import hcl2

def terraform_to_json(terraform_content):
    """
    Convert Terraform HCL to JSON format.
    """
    
    try:
        # Remove comments from Terraform content
        terraform_content = remove_terraform_comments(terraform_content)
        
        # Parse HCL content
        hcl_dict = hcl2.loads(terraform_content)
        
        # Extract resources
        resources = extract_resources(hcl_dict)
        
        # Extract variables
        variables = extract_variables(hcl_dict)
        
        # Extract outputs
        outputs = extract_outputs(hcl_dict)
        
        # Return structured JSON
        return {
            "terraform_version": hcl_dict.get('terraform', [{}])[0].get('required_version', 'unknown') if hcl_dict.get('terraform') else 'unknown',
            "variables": variables,
            "resources": resources,
            "outputs": outputs,
            "raw_config": hcl_dict  # Include raw parsed config for reference
        }
    
    except Exception as e:
        raise Exception(f"Failed to parse Terraform HCL: {str(e)}")


def remove_terraform_comments(terraform_content):
    """
    Remove comments from Terraform HCL content.
    Removes both single-line (#) and block comments (/* */).
    """
    lines = terraform_content.split('\n')
    cleaned_lines = []
    in_block_comment = False
    
    for line in lines:
        if in_block_comment:
            if '*/' in line:
                in_block_comment = False
                # Keep content after */
                line = line.split('*/', 1)[1]
            else:
                continue
        
        if '/*' in line:
            in_block_comment = True
            line = line.split('/*')[0]
        
        # Remove inline comments
        if '#' in line:
            # Check if # is inside a string
            in_string = False
            string_char = None
            for i, char in enumerate(line):
                if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                elif char == '#' and not in_string:
                    line = line[:i]
                    break
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_resources(hcl_dict):
    """
    Extract resources from parsed HCL dict.
    """
    resources = []
    
    if 'resource' in hcl_dict and isinstance(hcl_dict['resource'], list):
        for resource_block in hcl_dict['resource']:
            for resource_type_key, resource_configs in resource_block.items():
                resource_type = resource_type_key.strip('"')
                
                for resource_name_key, resource_properties in resource_configs.items():
                    resource_name = resource_name_key.strip('"')
                    
                    # Remove __is_block__ metadata
                    props = {k: v for k, v in resource_properties.items() if k != '__is_block__'}
                    
                    resource_obj = {
                        "type": resource_type,
                        "name": resource_name,
                        "properties": props
                    }
                    resources.append(resource_obj)
    
    return resources

def extract_variables(hcl_dict):
    """
    Extract variables from parsed HCL dict.
    """
    variables = {}
    
    if 'variable' in hcl_dict and isinstance(hcl_dict['variable'], list):
        for var_block in hcl_dict['variable']:
            for var_name_key, var_config in var_block.items():
                var_name = var_name_key.strip('"')
                # Remove __is_block__ metadata
                var_config_clean = {k: v for k, v in var_config.items() if k != '__is_block__'}
                variables[var_name] = var_config_clean
    
    return variables

def extract_outputs(hcl_dict):
    """
    Extract outputs from parsed HCL dict.
    """
    outputs = {}
    
    if 'output' in hcl_dict and isinstance(hcl_dict['output'], list):
        for output_block in hcl_dict['output']:
            for output_name_key, output_config in output_block.items():
                output_name = output_name_key.strip('"')
                # Remove __is_block__ metadata
                output_config_clean = {k: v for k, v in output_config.items() if k != '__is_block__'}
                outputs[output_name] = output_config_clean
    
    return outputs