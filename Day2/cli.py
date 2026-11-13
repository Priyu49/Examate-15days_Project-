from records import get_all_records, search_by_location, filter_by_ph_range

def cli_interface():
    while True:
        print("\n--- MitraMaati Soil CLI ---")
        print("1. View All Soil Records")
        print("2. Search by Location")
        print("3. Filter by pH Range")
        print("4. Exit")
        choice = input("Select an option: ")
        
        if choice == "1":
            for r in get_all_records():
                print(r)
        elif choice == "2":
            loc = input("Enter location (e.g., Pune): ")
            results = search_by_location(loc)
            for r in results:
                print(r)
        elif choice == "3":
            min_p = float(input("Min pH: "))
            max_p = float(input("Max pH: "))
            results = filter_by_ph_range(min_p, max_p)
            for r in results:
                print(r)
        elif choice == "4":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    cli_interface()