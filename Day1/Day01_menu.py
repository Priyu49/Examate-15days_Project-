from Day01_Intro import print_intro

def main_menu():
    while True:
        print("\n--- MitraMaati Main Menu ---")
        print("1. About MitraMaati")
        print("2. Sample Questions")
        print("3. Check Soil pH Rule")
        print("0. Exit")
        
        choice = input("Enter your choice (0-3): ")
        
        if choice == "1":
            print_intro()
        elif choice == "2":
            print("\nSample Questions:")
            print("- What is the ideal range for Nitrogen?")
            print("- How do I correct acidic soil pH?")
        elif choice == "3":
            ph = float(input("Enter soil pH to test: "))
            if ph < 6.0:
                print("Rule Check: Soil is Acidic. Apply agricultural lime.")
            elif ph > 8.0:
                print("Rule Check: Soil is Alkaline. Apply gypsum.")
            else:
                print("Rule Check: Soil pH is optimal/balanced.")
        elif choice == "0":
            print("Exiting MitraMaati. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 0, 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()