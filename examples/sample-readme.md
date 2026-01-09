# Invoice Automation System

> Automate invoice processing with OCR, validation, and ERP integration.

## Overview

Small businesses spend 10+ hours per week on manual invoice processing. This system cuts that to minutes by automating data extraction, validation, and entry.

## Key Features

- **OCR Extraction** - Pull invoice data from PDFs and images automatically
- **Validation Rules** - Check for duplicates, amount thresholds, and vendor matches
- **ERP Integration** - Push validated invoices directly to QuickBooks or Xero
- **Approval Workflow** - Route exceptions to the right approver
- **Audit Trail** - Complete history of every invoice action
- **Batch Processing** - Handle hundreds of invoices in one run

## Tech Stack

- Python 3.11
- Tesseract OCR
- PostgreSQL
- FastAPI
- Redis (job queue)
- Docker

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose up -d`
4. Access the dashboard at `http://localhost:8080`
5. Upload your first batch of invoices

## Roadmap

- Invoice template learning (done)
- Multi-currency support (done)
- Vendor auto-matching (done)
- Machine learning classification (planned)
- Mobile approval app (planned)
- Slack notifications (planned)

## Architecture

The system uses a three-stage pipeline:

- **Ingestion** - Files uploaded via API or watched folder
- **Processing** - OCR extraction, field mapping, validation
- **Output** - ERP push, approval routing, or rejection

## Contact

**Built by:** True North Data Strategies
**Email:** jacob@truenorthstrategyops.com
**GitHub:** github.com/truenorthdatastrategies

## License

MIT License
