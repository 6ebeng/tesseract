#!/usr/bin/env python3
"""
Phase 6 Incremental Training Workflow

Manages incremental corpus expansion with evaluation after each batch.
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class IncrementalTrainingManager:
    """Manage incremental training batches."""
    
    def __init__(self, base_corpus: str, work_dir: str = "work"):
        self.base_corpus = Path(base_corpus)
        self.work_dir = Path(work_dir)
        self.corpus_dir = self.work_dir / "corpus"
        self.output_dir = self.work_dir / "output"
        self.progress_file = Path("PHASE6_PROGRESS.md")
        
        if not self.base_corpus.exists():
            print(f"❌ Base corpus not found: {self.base_corpus}")
            sys.exit(1)
    
    def create_batch(self, batch_num: int, new_lines_file: str, lines_to_add: int = 500) -> Path:
        """
        Create a new training batch by adding lines to base corpus.
        
        Args:
            batch_num: Batch number (1, 2, 3, ...)
            new_lines_file: File containing new lines to add
            lines_to_add: Number of lines to add (default 500)
        
        Returns:
            Path to new batch corpus file
        """
        new_lines_path = Path(new_lines_file)
        if not new_lines_path.exists():
            print(f"❌ New lines file not found: {new_lines_path}")
            sys.exit(1)
        
        # Read base corpus
        with open(self.base_corpus, 'r', encoding='utf-8') as f:
            base_lines = [line.strip() for line in f if line.strip()]
        
        # Read new lines
        with open(new_lines_path, 'r', encoding='utf-8') as f:
            new_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Take requested number of lines
        lines_to_add_actual = min(lines_to_add, len(new_lines))
        batch_lines = new_lines[:lines_to_add_actual]
        
        # Check for duplicates with base corpus
        base_set = set(base_lines)
        unique_batch_lines = [line for line in batch_lines if line not in base_set]
        duplicates_found = lines_to_add_actual - len(unique_batch_lines)
        
        if duplicates_found > 0:
            print(f"⚠️  Removed {duplicates_found} duplicate lines")
        
        # Combine
        combined_lines = base_lines + unique_batch_lines
        
        # Save batch corpus
        batch_file = self.corpus_dir / f"ckb_phase6_batch{batch_num}.training_text"
        with open(batch_file, 'w', encoding='utf-8') as f:
            for line in combined_lines:
                f.write(line + '\n')
        
        print(f"\n✅ Created Batch {batch_num}")
        print(f"   Base lines: {len(base_lines):,}")
        print(f"   New lines: {len(unique_batch_lines):,}")
        print(f"   Total lines: {len(combined_lines):,}")
        print(f"   Saved to: {batch_file}")
        
        return batch_file
    
    def check_quality(self, corpus_file: Path) -> Dict:
        """Run quality checker on corpus and return results."""
        print(f"\n🔍 Checking quality of {corpus_file.name}...")
        
        result = subprocess.run(
            ['python3', 'tools/corpus_quality_checker.py', str(corpus_file)],
            cwd=self.work_dir,
            capture_output=True,
            text=True
        )
        
        # Parse output for key metrics
        output = result.stdout
        
        # Extract key metrics (simplified parsing)
        metrics = {
            'checked': True,
            'output': output
        }
        
        return metrics
    
    def activate_batch(self, batch_file: Path):
        """Activate batch corpus for training."""
        target_file = self.corpus_dir / "ckb.training_text"
        shutil.copy(batch_file, target_file)
        print(f"✅ Activated: {batch_file.name} → ckb.training_text")
    
    def train_batch(self, batch_num: int) -> bool:
        """
        Train model with current batch.
        
        Returns:
            True if training succeeded
        """
        print(f"\n🔨 Training Batch {batch_num}...")
        print("   This will take several hours...")
        print("   Running: ./run_training.ps1 -Mode GenerateTrain")
        
        # Note: This would actually run the training in production
        print("\n⚠️  MANUAL STEP REQUIRED:")
        print("   Please run in PowerShell:")
        print("   PS> cd c:\\tesseract")
        print("   PS> .\\run_training.ps1 -Mode GenerateTrain")
        print("\n   After training completes, run evaluation:")
        print("   PS> wsl -d Ubuntu -- bash -lc \"cd /mnt/c/tesseract/work && python3 tools/eval_real_cer.py\"")
        print("\n   Then run this script again with --evaluate flag")
        
        return False  # Manual training required
    
    def record_results(self, batch_num: int, lines: int, accuracy: float, cer: float):
        """Record batch training results."""
        timestamp = datetime.now().isoformat()
        
        result_entry = {
            'batch': batch_num,
            'lines': lines,
            'accuracy': accuracy,
            'cer': cer,
            'timestamp': timestamp
        }
        
        # Append to results file
        results_file = self.output_dir / "phase6_results.json"
        results = []
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
        
        results.append(result_entry)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update progress markdown
        self.update_progress_doc(results)
        
        print(f"\n📊 Batch {batch_num} Results:")
        print(f"   Lines: {lines:,}")
        print(f"   Accuracy: {accuracy:.2f}%")
        print(f"   CER: {cer:.4f}")
    
    def update_progress_doc(self, results: List[Dict]):
        """Update PHASE6_PROGRESS.md with latest results."""
        content = ["# Phase 6: Incremental Training Progress\n\n"]
        content.append(f"**Last updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        content.append("## Training Results\n\n")
        content.append("| Batch | Lines | Accuracy | CER | Change | Date |\n")
        content.append("|-------|-------|----------|-----|--------|------|\n")
        
        prev_acc = 72.19  # Phase 4 baseline
        for r in results:
            change = r['accuracy'] - prev_acc
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            date_str = r['timestamp'][:10]
            content.append(f"| {r['batch']} | {r['lines']:,} | {r['accuracy']:.2f}% | {r['cer']:.4f} | {change_str} | {date_str} |\n")
            prev_acc = r['accuracy']
        
        content.append("\n## Progress Chart\n\n")
        content.append("```\n")
        content.append("Accuracy Progress:\n")
        for r in results:
            bar = "█" * int(r['accuracy'])
            content.append(f"Batch {r['batch']:2d} ({r['lines']:5,} lines): {bar} {r['accuracy']:.2f}%\n")
        content.append("```\n")
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            f.writelines(content)
        
        print(f"📄 Updated: {self.progress_file}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Phase 6 Incremental Training Manager")
        print("=" * 50)
        print("\nUsage:")
        print("  Create batch:  python3 incremental_training.py create <batch_num> <new_lines_file> [lines_to_add]")
        print("  Record result: python3 incremental_training.py record <batch_num> <lines> <accuracy> <cer>")
        print("\nExamples:")
        print("  python3 incremental_training.py create 1 kurdish_news.txt 500")
        print("  python3 incremental_training.py record 1 3821 72.5 0.275")
        sys.exit(1)
    
    command = sys.argv[1]
    
    manager = IncrementalTrainingManager(
        base_corpus="work/corpus/ckb_phase4.training_text.backup"
    )
    
    if command == "create":
        if len(sys.argv) < 4:
            print("❌ Usage: create <batch_num> <new_lines_file> [lines_to_add]")
            sys.exit(1)
        
        batch_num = int(sys.argv[2])
        new_lines_file = sys.argv[3]
        lines_to_add = int(sys.argv[4]) if len(sys.argv) > 4 else 500
        
        batch_file = manager.create_batch(batch_num, new_lines_file, lines_to_add)
        manager.check_quality(batch_file)
        manager.activate_batch(batch_file)
        manager.train_batch(batch_num)
    
    elif command == "record":
        if len(sys.argv) < 6:
            print("❌ Usage: record <batch_num> <lines> <accuracy> <cer>")
            sys.exit(1)
        
        batch_num = int(sys.argv[2])
        lines = int(sys.argv[3])
        accuracy = float(sys.argv[4])
        cer = float(sys.argv[5])
        
        manager.record_results(batch_num, lines, accuracy, cer)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Valid commands: create, record")
        sys.exit(1)


if __name__ == '__main__':
    main()
