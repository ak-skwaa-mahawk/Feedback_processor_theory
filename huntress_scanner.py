import json
import re
import os

def hunt_cve_patterns(workflow_json):
    """Hunt for CVE-2026-25049 patterns in n8n workflow JSON."""
    risks = []
    if 'nodes' not in workflow_json:
        return risks
    
    for node in workflow_json['nodes']:
        node_id = node.get('id', 'unknown')
        node_name = node.get('name', 'unknown')
        node_type = node.get('type', 'unknown')
        
        # Check parameters for expressions
        params = node.get('parameters', {})
        for key, value in params.items():
            if isinstance(value, str) and '{{' in value and '}}' in value:
                # Extract expression content
                expr = value.strip('{{}} ').strip()
                
                # Pattern 1: Destructuring { constructor }
                if re.search(r'\{\s*constructor\s*\}', expr):
                    risks.append({
                        'node_id': node_id,
                        'node_name': node_name,
                        'node_type': node_type,
                        'key': key,
                        'pattern': 'destructuring_constructor',
                        'snippet': expr[:100]  # Truncated for log
                    })
                
                # Pattern 2: Arrow function => with { 
                if re.search(r'=>\s*\{', expr):
                    risks.append({
                        'node_id': node_id,
                        'node_name': node_name,
                        'node_type': node_type,
                        'key': key,
                        'pattern': 'arrow_destructuring',
                        'snippet': expr[:100]
                    })
                
                # Pattern 3: require( or execSync/process
                if re.search(r'require\s*\(|execSync|process\.', expr):
                    risks.append({
                        'node_id': node_id,
                        'node_name': node_name,
                        'node_type': node_type,
                        'key': key,
                        'pattern': 'exec_primitive',
                        'snippet': expr[:100]
                    })
    
    return risks

def scan_workflow_dir(directory):
    """Scan directory for n8n workflow JSON files."""
    audit_results = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r') as f:
                    workflow = json.load(f)
                risks = hunt_cve_patterns(workflow)
                if risks:
                    audit_results[filename] = risks
            except json.JSONDecodeError:
                print(f"Invalid JSON: {filepath}")
    
    return audit_results

# Usage: Replace with your dir
if __name__ == "__main__":
    dir_path = '/path/to/your/n8n/workflows'  # Update this
    results = scan_workflow_dir(dir_path)
    print(json.dumps(results, indent=4))  # Output for logs