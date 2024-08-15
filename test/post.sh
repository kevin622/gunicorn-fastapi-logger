#!/bin/bash
curl localhost:8000 -H "Content-Type: application/json" -d"
{
    \"name\": \"Clothes\",
    \"description\": \"Wearable\",
    \"category\": \"human\",
    \"price\": 9.99,
    \"tax\": 0.99
}"
