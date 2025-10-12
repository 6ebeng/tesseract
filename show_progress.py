#!/usr/bin/env python3
"""
Visual progress tracker for Option D training phases
Shows real-time status and estimates
"""

import os
import time
import glob
from datetime import datetime, timedelta

def count_files(pattern):
    """Count files matching pattern"""
    return len(glob.glob(pattern))

def get_file_age(filepath):
    """Get file age in minutes"""
    if os.path.exists(filepath):
        age = time.time() - os.path.getmtime(filepath)
        return age / 60  # minutes
    return None

def estimate_completion(current, total, elapsed_minutes):
    """Estimate time remaining"""
    if current == 0:
        return "Unknown"
    
    rate = elapsed_minutes / current
    remaining = (total - current) * rate
    
    if remaining < 60:
        return f"{int(remaining)} minutes"
    else:
        hours = remaining / 60
        return f"{hours:.1f} hours"

def show_progress():
    """Show current progress"""
    
    print("=" * 80)
    print("🚀 OPTION D - PHASE 1 TRAINING PROGRESS")
    print("=" * 80)
    print()
    
    # Check data generation
    box_files = count_files("work/training_output/ground_truth/*.box")
    tif_files = count_files("work/training_output/ground_truth/*.tif")
    lstmf_files = count_files("work/training_output/ground_truth/*.lstmf")
    
    expected_files = 81  # 9 fonts × 3 exposures × 3 scripts
    
    print("📊 DATA GENERATION:")
    print("-" * 80)
    print(f"BOX files:   {box_files}/{expected_files}   ", end="")
    print("█" * (box_files * 40 // expected_files) + "░" * (40 - box_files * 40 // expected_files))
    print(f"TIF files:   {tif_files}/{expected_files}   ", end="")
    print("█" * (tif_files * 40 // expected_files) + "░" * (40 - tif_files * 40 // expected_files))
    print(f"LSTMF files: {lstmf_files}/{expected_files}   ", end="")
    print("█" * (lstmf_files * 40 // expected_files) + "░" * (40 - lstmf_files * 40 // expected_files))
    
    if lstmf_files == expected_files:
        print("\n✅ Data generation COMPLETE!")
    elif lstmf_files > 0:
        print(f"\n⏳ Data generation in progress... {lstmf_files}/{expected_files} done")
    else:
        print("\n⏸️ Data generation not started or just beginning")
    
    print()
    
    # Check training logs
    logs = {
        'fas': 'work/training_output/logs/lstmtraining_ckb_from_fas.log',
        'ara': 'work/training_output/logs/lstmtraining_ckb_from_ara.log',
        'eng': 'work/training_output/logs/lstmtraining_ckb_from_eng.log'
    }
    
    print("🎓 MODEL TRAINING:")
    print("-" * 80)
    
    for model, logfile in logs.items():
        if os.path.exists(logfile):
            # Get last line with iteration info
            try:
                with open(logfile, 'r') as f:
                    lines = f.readlines()
                    
                # Find last iteration line
                last_iter = None
                bcer = None
                for line in reversed(lines):
                    if 'Iteration' in line:
                        last_iter = line.strip()
                        break
                
                if last_iter:
                    # Extract iteration number
                    parts = last_iter.split()
                    for i, part in enumerate(parts):
                        if part == 'Iteration':
                            iter_num = parts[i+1].rstrip(',')
                            print(f"{model.upper()}: Iteration {iter_num} ", end="")
                            
                            # Try to find BCER
                            for j, p in enumerate(parts):
                                if 'BCER' in p or 'training' in p:
                                    if j+1 < len(parts):
                                        bcer_val = parts[j+1].rstrip('%,')
                                        print(f"(BCER: {bcer_val}%)")
                                        break
                            else:
                                print()
                            break
                else:
                    print(f"{model.upper()}: Starting...")
            except Exception as e:
                print(f"{model.upper()}: Log file exists but unreadable")
        else:
            print(f"{model.upper()}: Not started yet")
    
    print()
    
    # Check models
    models = glob.glob("work/training_output/model/ckb_from_*.traineddata")
    
    print("✨ COMPLETED MODELS:")
    print("-" * 80)
    if models:
        for model in models:
            name = os.path.basename(model)
            size = os.path.getsize(model) / 1024 / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(model))
            print(f"✅ {name:<40} {size:>6.2f} MB  {mtime:%H:%M:%S}")
    else:
        print("⏸️ No models completed yet")
    
    print()
    
    # Overall status
    print("=" * 80)
    print("📈 OVERALL STATUS:")
    print("=" * 80)
    
    if lstmf_files < expected_files:
        phase = "Data Generation"
        pct = (lstmf_files / expected_files) * 100
    elif len(models) == 0:
        phase = "Training (Starting)"
        pct = 0
    elif len(models) < 3:
        phase = f"Training ({len(models)}/3 models)"
        pct = 33 + (len(models) * 22)
    else:
        phase = "Complete"
        pct = 100
    
    print(f"Current Phase: {phase}")
    print(f"Progress: {pct:.1f}% ", end="")
    print("█" * int(pct // 2.5) + "░" * (40 - int(pct // 2.5)))
    
    print()
    print("=" * 80)
    print(f"Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 80)

if __name__ == '__main__':
    show_progress()
