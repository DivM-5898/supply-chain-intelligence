"""
Supplier Evaluation API Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import sys
import os
import pandas as pd
import tempfile

# Add parent directory to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_path)

from services.supplier_scoring import get_supplier_scoring_service
from api.models import SupplierEvaluationRequest, SupplierEvaluationResponse

router = APIRouter()


@router.post("/evaluate", response_model=SupplierEvaluationResponse)
async def evaluate_suppliers(request: SupplierEvaluationRequest):
    """Evaluate suppliers using ML models"""
    try:
        supplier_scoring_service = get_supplier_scoring_service()
        
        # Ensure models are loaded
        if not supplier_scoring_service.models:
            try:
                supplier_scoring_service.load_models()
            except FileNotFoundError as e:
                # Models don't exist, try to train them
                raise HTTPException(
                    status_code=503,
                    detail=f"Models not found. Please train models first. Error: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error loading models: {str(e)}"
                )
        
        # Validate model type
        available_models = supplier_scoring_service.get_available_models()
        if not available_models:
            raise HTTPException(
                status_code=503,
                detail="No models available. Please train models first."
            )
        
        if request.model_type not in available_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model_type}' not available. Available models: {available_models}"
            )
        
        # Load and predict
        results_df = supplier_scoring_service.predict_supplier_score(
            request.supplier_ids,
            request.model_type
        )
        
        if results_df.empty:
            raise HTTPException(
                status_code=404, 
                detail="No suppliers found matching the criteria. Please check your supplier data."
            )
        
        results = results_df.to_dict('records')
        
        return SupplierEvaluationResponse(
            results=results,
            model_type=request.model_type,
            total_suppliers=len(results)
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Required data file not found: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/compare-models")
async def compare_models(supplier_ids: Optional[str] = None, models: Optional[str] = None):
    """Compare multiple models"""
    try:
        supplier_scoring_service = get_supplier_scoring_service()
        ids_list = supplier_ids.split(',') if supplier_ids else None
        model_list = models.split(',') if models else None
        comparison_df = supplier_scoring_service.compare_models(ids_list, model_list)
        
        return {
            "results": comparison_df.to_dict('records'),
            "total_suppliers": len(comparison_df),
            "models_compared": model_list or ['xgboost', 'random_forest', 'gradient_boosting']
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/available-models")
async def get_available_models():
    """Get list of available models"""
    try:
        supplier_scoring_service = get_supplier_scoring_service()
        available_models = supplier_scoring_service.get_available_models()
        
        # If no models available, return helpful message
        if not available_models:
            return {
                "available_models": [],
                "total_models": 0,
                "message": "No models found. Please train models first by running: python backend/train_models.py"
            }
        
        return {
            "available_models": available_models,
            "total_models": len(available_models)
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in get_available_models endpoint: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error getting available models: {str(e)}")


@router.get("/feature-importance/{model_type}")
async def get_feature_importance(model_type: str):
    """Get feature importance for a model"""
    try:
        supplier_scoring_service = get_supplier_scoring_service()
        
        if supplier_scoring_service.models.get(model_type) is None:
            supplier_scoring_service.load_models()
        
        model = supplier_scoring_service.models.get(model_type)
        if model is None:
            raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
        
        # Check if model has feature_importances_ attribute
        if not hasattr(model, 'feature_importances_'):
            # Return a helpful message instead of error
            return {
                "model_type": model_type,
                "message": f"Feature importance is not available for {model_type} model type. Use tree-based models (XGBoost, Random Forest, Gradient Boosting, AdaBoost, Ensemble) for feature importance.",
                "available_models_with_importance": ['xgboost', 'random_forest', 'gradient_boosting', 'adaboost', 'ensemble'],
                "feature_importance": {}
            }
        
        importance = model.feature_importances_
        feature_importance = dict(zip(supplier_scoring_service.feature_columns, importance.tolist()))
        
        return {
            "model_type": model_type,
            "feature_importance": feature_importance
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/upload-and-evaluate")
async def upload_and_evaluate(
    file: UploadFile = File(...),
    model_type: str = Form(default="xgboost"),
    top_n: Optional[int] = Form(default=None)
):
    """
    Upload CSV/Excel file and evaluate suppliers
    
    Expected file format: CSV or Excel with supplier data columns matching the training data format
    Required columns: supplier_id, on_time_delivery_rate, quality_score, defect_rate, 
                      credit_score, debt_to_equity, profit_margin, years_in_business, 
                      utilization_rate, geopolitical_risk_score, esg_score, compliance_score, etc.
    """
    try:
        # Validate file type
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload CSV or Excel (.xlsx, .xls) file."
            )
        
        # Read file content
        contents = await file.read()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(contents)
            tmp_path = tmp_file.name
        
        try:
            # Load data based on file type
            if file_extension == 'csv':
                df = pd.read_csv(tmp_path)
            else:
                df = pd.read_excel(tmp_path)
            
            # Validate required columns
            required_cols = ['supplier_id']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required columns: {', '.join(missing_cols)}"
                )
            
            supplier_scoring_service = get_supplier_scoring_service()
            
            # Ensure models are loaded
            try:
                if not supplier_scoring_service.models:
                    supplier_scoring_service.load_models()
            except Exception as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to load models: {str(e)}. Please ensure models are trained."
                )
            
            # Validate model type
            try:
                available_models = supplier_scoring_service.get_available_models()
                if not available_models:
                    raise HTTPException(
                        status_code=503,
                        detail="No models available. Please train models first."
                    )
                if model_type not in available_models:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Model '{model_type}' not available. Available models: {available_models}"
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error checking available models: {str(e)}"
                )
            
            # Define required columns and defaults for missing ones
            required_base_columns = {
                'supplier_id': None,  # Must be present
                'on_time_delivery_rate': 0.85,
                'quality_score': 0.75,
                'defect_rate': 0.02,
                'credit_score': 650,
                'debt_to_equity': 1.0,
                'profit_margin': 0.10,
                'years_in_business': 10,
                'utilization_rate': 0.80,
                'geopolitical_risk_score': 0.50,
                'esg_score': 0.70,
                'compliance_score': 0.80,
                'has_erp_system': False,
                'certifications': 'None',
                'avg_delivery_time_days': 14.0
            }
            
            # Check for required column
            if 'supplier_id' not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required column: 'supplier_id'. Please check your file format."
                )
            
            # Add missing columns with defaults
            missing_columns = []
            for col, default_value in required_base_columns.items():
                if col not in df.columns and default_value is not None:
                    df[col] = default_value
                    missing_columns.append(col)
            
            # Log missing columns for debugging
            if missing_columns:
                print(f"Added default values for missing columns: {', '.join(missing_columns)}")
            
            # Prepare features from uploaded data
            try:
                from utils.preprocessing import preprocessor
                df_processed, feature_cols = preprocessor.prepare_supplier_features(df, use_advanced_features=False)
            except KeyError as e:
                missing_col = str(e).strip("'")
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing uploaded data: missing column '{missing_col}'. Required columns: {list(required_base_columns.keys())}"
                )
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Preprocessing error: {error_trace}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing uploaded data: {str(e)}. Please check your file format and columns."
                )
            
            # Get supplier IDs
            supplier_ids = df_processed['supplier_id'].tolist()
            
            # Prepare features for prediction
            try:
                # Ensure all feature columns exist
                missing_features = [col for col in feature_cols if col not in df_processed.columns]
                if missing_features:
                    # Fill missing features with 0
                    for col in missing_features:
                        df_processed[col] = 0
                
                X = df_processed[feature_cols].fillna(0)
                
                # Get model and scale if needed
                model = supplier_scoring_service.models[model_type]
                if model_type in supplier_scoring_service.scalers:
                    X = supplier_scoring_service.scalers[model_type].transform(X)
                
                # Make predictions
                predictions = model.predict(X)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error making predictions: {str(e)}. Please check your data format matches the training data."
                )
            
            # Create results DataFrame
            results_df = pd.DataFrame({
                'supplier_id': supplier_ids,
                'predicted_score': predictions,
                'model_type': model_type
            })
            
            # Sort by score descending
            results_df = results_df.sort_values('predicted_score', ascending=False)
            results_df['rank'] = range(1, len(results_df) + 1)
            
            # Apply top_n filter if specified
            if top_n:
                results_df = results_df.head(top_n)
            
            # Convert to dict
            results = results_df.to_dict('records')
            
            return {
                "results": results,
                "model_type": model_type,
                "total_suppliers": len(results),
                "file_name": file.filename,
                "message": f"Successfully evaluated {len(results)} suppliers from uploaded file"
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=f"Error processing file: {error_detail}")
