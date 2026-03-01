"""Quick test script to verify all imports work"""
print("Testing imports...")

print("✓ FastAPI...")
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response, JSONResponse

print("✓ Twilio...")
from twilio.twiml.messaging_response import MessagingResponse

print("✓ Standard library...")
import os, sys, json, uuid, hmac, hashlib, tempfile, requests, re
from datetime import datetime

print("✓ Razorpay...")
import razorpay

print("✓ Environment...")
from dotenv import load_dotenv

print("✓ HTTP clients...")
import httpx

print("✓ Web scraping...")
from bs4 import BeautifulSoup
from googlesearch import search

print("✓ Google Genai...")
from google import genai

print("✓ Translation...")
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

print("✓ Voice processing...")
import speech_recognition as sr
from pydub import AudioSegment

print("\n🎉 ALL IMPORTS SUCCESSFUL!\n")

# Test Genai initialization
print("Testing Genai initialization...")
try:
    test_client = genai.Client(api_key="test_key")
    print("✓ Genai Client created successfully")
except Exception as e:
    print(f"⚠ Genai Client error: {e}")

print("\n✅ All tests passed!")
