#!/usr/bin/env python
"""
Test script for Symptom Triage Engine
Run: python test_triage.py
"""

import sys
import os
import json

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from api.triage import (
    detect_symptom_case,
    check_emergency_combination,
    run_triage,
    get_triage_summary
)


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_case(name, symptoms_list):
    print(f"🧪 Test: {name}")
    print(f"📝 Symptoms: {symptoms_list}")
    print()
    
    # Run triage
    result = run_triage(symptoms_list)
    
    # Print JSON output
    print("📊 JSON Output:")
    print(json.dumps(result, indent=2))
    print()
    
    # Print user-facing message
    print("💬 User-Facing Message:")
    print(get_triage_summary(result))
    print("\n" + "-" * 80 + "\n")


def main():
    print_section("SYMPTOM TRIAGE ENGINE - TEST SUITE")
    
    # Test 1: Emergency - Immediate Detection
    print_section("TEST 1: Emergency Case (Immediate Detection)")
    test_case(
        "Chest pain with breathing difficulty",
        ["I have severe chest pain and I can't breathe"]
    )
    
    # Test 2: Emergency - Dizziness + Chest Pain
    print_section("TEST 2: Emergency Case (Multiple Symptoms)")
    test_case(
        "Chest pain with dizziness",
        ["I feel dizzy and have chest pressure"]
    )
    
    # Test 3: Routine - High Severity
    print_section("TEST 3: Routine Case (High Severity)")
    test_case(
        "Spreading rash",
        [
            "I have an itchy rash on my arm",
            "About 3 days",
            "It's spreading and getting worse",
            "Yes, I used a new soap"
        ]
    )
    
    # Test 4: Routine - Low Severity
    print_section("TEST 4: Routine Case (Low Severity)")
    test_case(
        "Mild rash",
        [
            "I have a mild rash",
            "2 days",
            "It's staying in one area and not spreading",
            "No new products"
        ]
    )
    
    # Test 5: Routine - Medium Severity
    print_section("TEST 5: Routine Case (Medium Severity)")
    test_case(
        "Rash with mild fever",
        [
            "I have a skin rash and mild fever",
            "Started yesterday",
            "The rash is on my chest",
            "No known allergens"
        ]
    )
    
    # Test 6: Unknown Symptoms (Fallback)
    print_section("TEST 6: Unknown Symptoms (Fallback)")
    test_case(
        "Headache",
        [
            "I have a headache",
            "Since this morning",
            "About a 5 out of 10",
            "No other symptoms"
        ]
    )
    
    # Test 7: Emergency - Single Keyword
    print_section("TEST 7: Emergency Case (Single Keyword)")
    test_case(
        "Shortness of breath",
        ["I'm having shortness of breath"]
    )
    
    # Test 8: Detection Tests
    print_section("TEST 8: Keyword Detection Tests")
    
    test_inputs = [
        "I have chest pain",
        "I can't breathe properly",
        "I feel dizzy",
        "I have a rash",
        "My skin is itching",
        "I have a mild fever",
        "I have a headache",
    ]
    
    for test_input in test_inputs:
        case, keywords = detect_symptom_case(test_input)
        is_emergency, combo = check_emergency_combination(test_input)
        
        print(f"Input: '{test_input}'")
        print(f"  → Detected Case: {case}")
        print(f"  → Matched Keywords: {keywords}")
        print(f"  → Emergency Combo: {is_emergency} {combo if is_emergency else ''}")
        print()
    
    print_section("TEST SUITE COMPLETE")
    print("✅ All tests executed successfully!")
    print("\nNote: Review outputs to ensure they match expected behavior.")


if __name__ == "__main__":
    main()
