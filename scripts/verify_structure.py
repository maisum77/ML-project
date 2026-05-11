#!/usr/bin/env python3
"""Verify the SocialPulse AI project structure is correctly set up."""

import os
import sys

REQUIRED_DIRS = [
    "backend/app/api",
    "backend/app/core",
    "backend/app/models",
    "backend/app/services",
    "backend/app/schemas",
    "backend/tests",
    "data_collection",
    "data_processing",
    "ml_models/fake_news",
    "ml_models/sentiment",
    "ml_models/topic_modeling",
    "fact_check",
    "frontend/app",
    "frontend/components",
    "frontend/styles",
    "frontend/lib",
    "tests",
    "scripts",
    "results",
    "report",
]

REQUIRED_FILES = [
    "requirements.txt",
    "requirements-ml.txt",
    ".env.example",
    "amplify.yml",
    "template.yaml",
    "README.md",
    "QUICKSTART.md",
    "start.bat",
    "start.sh",
    ".gitignore",
    "backend/lambda_handler.py",
    "backend/app/main.py",
    "backend/app/core/config.py",
    "backend/app/core/database.py",
    "backend/app/core/dynamodb.py",
    "backend/app/core/security.py",
    "backend/app/api/router.py",
    "backend/app/api/trending.py",
    "backend/app/api/sentiment.py",
    "backend/app/api/classify.py",
    "backend/app/api/feed.py",
    "backend/app/api/export.py",
    "backend/app/api/propagation.py",
    "backend/app/api/geo.py",
    "backend/app/api/authority.py",
    "backend/app/schemas/posts.py",
    "backend/app/schemas/responses.py",
    "backend/app/services/trending_service.py",
    "backend/app/services/sentiment_service.py",
    "backend/app/services/classification_service.py",
    "backend/app/services/factcheck_service.py",
    "backend/app/services/propagation_service.py",
    "backend/app/services/geo_service.py",
    "backend/app/services/authority_service.py",
    "backend/app/models/authority_sources.py",
    "data/location_mappings.py",
    "data_collection/__init__.py",
    "data_collection/reddit_collector.py",
    "data_collection/twitter_collector.py",
    "data_collection/deduplication.py",
    "data_processing/__init__.py",
    "data_processing/preprocessor.py",
    "data_processing/pipeline.py",
    "ml_models/__init__.py",
    "ml_models/train_all.py",
    "ml_models/evaluate.py",
    "ml_models/ablation.py",
    "ml_models/case_study.py",
    "ml_models/fake_news/__init__.py",
    "ml_models/fake_news/predict.py",
    "ml_models/fake_news/train.py",
    "ml_models/sentiment/__init__.py",
    "ml_models/sentiment/predict.py",
    "ml_models/sentiment/train.py",
    "ml_models/topic_modeling/__init__.py",
    "ml_models/topic_modeling/predict.py",
    "ml_models/topic_modeling/train.py",
    "fact_check/__init__.py",
    "fact_check/google_factcheck.py",
    "fact_check/claimbuster.py",
    "fact_check/verifier.py",
    "frontend/package.json",
    "frontend/next.config.js",
    "frontend/app/layout.tsx",
    "frontend/app/page.tsx",
    "frontend/lib/api.ts",
    "frontend/components/TrendingTopics.tsx",
    "frontend/components/FakeRealChart.tsx",
    "frontend/components/SentimentTimeline.tsx",
    "frontend/components/PostExplorer.tsx",
    "frontend/components/LiveFeed.tsx",
    "frontend/components/GlobeView.tsx",
    "frontend/components/PropagationGraph.tsx",
    "frontend/components/AuthorityBadge.tsx",
    "frontend/styles/globals.css",
    "tests/test_api.py",
    "tests/test_preprocessing.py",
    "tests/test_deduplication.py",
    "tests/test_ml_models.py",
    "scripts/create_dynamodb_tables.py",
    "report/report.tex",
]


def check_structure():
    missing_dirs = []
    missing_files = []

    for d in REQUIRED_DIRS:
        if not os.path.isdir(d):
            missing_dirs.append(d)

    for f in REQUIRED_FILES:
        if not os.path.isfile(f):
            missing_files.append(f)

    if missing_dirs or missing_files:
        print("PROJECT STRUCTURE CHECK: FAILED")
        print()
        if missing_dirs:
            print("Missing directories:")
            for d in missing_dirs:
                print(f"  - {d}")
        if missing_files:
            print("Missing files:")
            for f in missing_files:
                print(f"  - {f}")
        return False
    else:
        print("PROJECT STRUCTURE CHECK: PASSED")
        print(f"  {len(REQUIRED_DIRS)} directories OK")
        print(f"  {len(REQUIRED_FILES)} files OK")
        return True


if __name__ == "__main__":
    success = check_structure()
    sys.exit(0 if success else 1)
