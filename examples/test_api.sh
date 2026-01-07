#!/bin/bash

# Skrypt testowy dla API Kalkulatora Podatkowego JDG

API_URL="http://localhost:8000"

echo "=========================================="
echo "Kalkulator Podatkowy JDG - Test API"
echo "=========================================="
echo ""

# 1. Health check
echo "1. Health check..."
curl -s "${API_URL}/health" | jq '.'
echo ""
echo ""

# 2. Root endpoint
echo "2. Root endpoint..."
curl -s "${API_URL}/" | jq '.'
echo ""
echo ""

# 3. Dostępne stawki ryczałtu
echo "3. Dostępne stawki ryczałtu..."
curl -s "${API_URL}/api/tax-rates" | jq '.'
echo ""
echo ""

# 4. Obliczenia - przykładowy request
echo "4. Obliczenia podatkowe (przykład)..."
echo "Wysyłanie POST /api/calculate..."

curl -s -X POST "${API_URL}/api/calculate" \
  -H "Content-Type: application/json" \
  -d @example_request.json | jq '.best_form, .best_form_description, .tax_scale.total_net_income, .linear_tax.total_net_income, .lump_sum.total_net_income'

echo ""
echo ""
echo "=========================================="
echo "Test zakończony"
echo "=========================================="
