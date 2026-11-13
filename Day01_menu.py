from Day01_Intro import print_intro

def main_menu():
    print_intro()
    while True:
        print("\n--- MitraMaati Main Menu ---")
        print("1. View Project Overview")
        print("2. Exit")
        choice = input("Enter your choice (1-2): ")
        
        if choice == "1":
            print("\nMitraMaati bridges soil test reports with actionable agricultural guidance.")
        elif choice == "2":
            print("Exiting MitraMaati. Happy farming!")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main_menu()