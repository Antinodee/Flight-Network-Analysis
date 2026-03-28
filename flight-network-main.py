# Flight Network Analysis - Main Project Runner
# This script runs all analysis steps in sequence

import os
import sys
import time
import importlib.util
import subprocess
import traceback

def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def run_script(script_path, script_name):
    """Run a Python script and handle any errors"""
    print_section_header(f"Running {script_name}")
    
    try:
        # Method 1: Import and run the script as a module
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"\n{script_name} completed successfully")
        return True
    except Exception as e:
        print(f"\nError running {script_name}:")
        print(traceback.format_exc())
        print("\nTrying alternative method...")
        
        try:
            # Method 2: Use subprocess to run the script
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout)
                print(f"\n{script_name} completed successfully")
                return True
            else:
                print(f"Error output: {result.stderr}")
                print(f"\n{script_name} failed")
                return False
        except Exception as e2:
            print(f"Both methods failed for {script_name}:")
            print(str(e2))
            return False

def main():
    """Run all flight network analysis scripts in sequence"""
    print_section_header("FLIGHT NETWORK ANALYSIS PROJECT")
    print("This script will run all analyses in sequence.\n")
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('report', exist_ok=True)
    
    # List of scripts to run in order
    scripts = [
        ("flight-network-setup.py", "Environment Setup"),
        ("flight-network-data-acquisition.py", "Data Acquisition"),
        ("flight-network-creation.py", "Network Creation"),
        ("flight-network-hub-analysis.py", "Hub Analysis"),
        ("flight-network-resilience.py", "Network Resilience Analysis"),
        ("flight-network-community.py", "Community Detection"),
        ("flight-network-seasonal.py", "Seasonal Pattern Analysis"),
        ("flight-network-report.py", "Report Generation")
    ]
    
    # Create script files from the artifacts
    print("Creating script files from artifacts...")
    
    # Extract scripts from the artifacts you've created
    artifact_ids = [
        "flight-network-setup",
        "flight-network-data-acquisition",
        "flight-network-creation",
        "flight-network-hub-analysis",
        "flight-network-resilience",
        "flight-network-community",
        "flight-network-seasonal",
        "flight-network-report"
    ]
    
    # For a real implementation, you'd read the artifact content
    # Since we can't directly access the artifacts in this script,
    # we'll assume they've been saved to files manually
    
    # Ask user if they want to run all scripts or select specific ones
    print("\nOptions:")
    print("1. Run all analysis steps")
    print("2. Run specific analysis steps")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "2":
        print("\nAvailable analysis steps:")
        for i, (_, name) in enumerate(scripts):
            print(f"{i+1}. {name}")
        
        selected = input("\nEnter step numbers to run (comma-separated, e.g., 1,3,5): ").strip()
        selected_indices = [int(x.strip()) - 1 for x in selected.split(",") if x.strip().isdigit()]
        
        # Filter scripts based on selection
        scripts = [scripts[i] for i in selected_indices if 0 <= i < len(scripts)]
    
    # Run each script in sequence
    start_time = time.time()
    success_count = 0
    
    for i, (script_file, script_name) in enumerate(scripts):
        print(f"\nStep {i+1}/{len(scripts)}: {script_name}")
        
        script_path = f"{script_file}"
        
        if run_script(script_path, script_name):
            success_count += 1
        
        # Small pause between scripts
        if i < len(scripts) - 1:
            print("\nWaiting 3 seconds before next step...")
            time.sleep(3)
    
    # Print summary
    elapsed_time = time.time() - start_time
    print_section_header("ANALYSIS COMPLETE")
    print(f"Successfully completed {success_count} out of {len(scripts)} steps")
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")
    
    if success_count == len(scripts):
        print("\nAll analysis steps completed successfully!")
        print("\nThe comprehensive report is available at: report/flight_network_analysis_report.html")
    else:
        print("\nSome analysis steps failed. Check the output above for details.")

if __name__ == "__main__":
    main()