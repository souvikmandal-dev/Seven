from Brain import Brain

brain = Brain()

print("Seven is starting...")

while  True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Seven is shutting down...")
        break
    else:
        # Here you can add the logic for Seven to respond to user input
        response = brain.talk(user_input)
        print(response)