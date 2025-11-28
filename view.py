def kati():
    print("\n\t\t--->>Welcome to the BasketBall League<<---")
    print("Press one of the following options:")
    print("1: View Teams")
    print("2: Create Team")
    print("3: Stats")
    print("4: Exit")
    valid_answers = ["1", "2", "3", "4"] 
    
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-4)")
        answer = input("Awaiting Response: ")
    return answer