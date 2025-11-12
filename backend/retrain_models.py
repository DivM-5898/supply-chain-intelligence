"""
Quick script to retrain models with correct features
"""
import sys
import os

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from services.supplier_scoring import SupplierScoringService

print("Retraining supplier scoring models...")
print("="*60)

service = SupplierScoringService()

try:
    results = service.train_all_models()
    print("\n[OK] Training complete!")
    print(f"\nResults:")
    for model_name, metrics in results.items():
        if isinstance(metrics, dict):
            r2 = metrics.get('r2', metrics.get('r2_score', 0))
            rmse = metrics.get('rmse', 0)
            print(f"  {model_name}: R2 = {r2:.4f}, RMSE = {rmse:.4f}")
        else:
            print(f"  {model_name}: {metrics}")
    
    print(f"\nModels saved to: {service.models_dir}")
    print("\nRestart the backend server to use the new models.")
except Exception as e:
    print(f"\n[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()

