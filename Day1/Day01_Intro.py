def print_intro():
    product = "MitraMaati"
    user = "Farmers & Agronomists"
    problem = "Soil nutrient imbalance and lack of localized fertilizer guidance"
    data_source = "Soil Health Card (SHC) Portal & IISS guidelines"
    
    print("=" * 60)
    print(f"Product    : {product}")
    print(f"User       : {user}")
    print(f"Problem    : {problem}")
    print(f"Data Source: {data_source}")
    print("=" * 60)

if __name__ == "__main__":
    print_intro()
    name = input("Enter your name: ")
    question = input("Enter your soil health question: ")
    print(f"Welcome {name}! We will analyze your query: '{question}'")