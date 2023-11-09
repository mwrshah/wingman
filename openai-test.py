from openai import OpenAI
client = OpenAI()

conversation =  """Jose: Can we get this invoice paid? INV2348""" 
information = input("Provide context now:")
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a customer support agent trained in responding to customers without promising resolution. If appropriate you can give them some assurance that their issue or request is being handled. Customers that reach out via email are either facing a technical issue or looking to get a request processed, and actioned."},
    {"role": "user", "content": f"""

Write a response to the last message from the customer in a conversation provided to you.  Make sure of the following:
-Be direct and use action oriented language.
-Don't be too wordy.
-Use a salutation like "Dear [Customer's First Name]"
-Only if there are no messages from the support team, and only messages from bots or customers,he first line should be Thank you for contacting [Product] Support team. I understand ...
-There should be no byline.
-The meat and bones of the reply should be based on the information provided to you as input. Draft a response considering that information and regurgitating it if appropriate.

I am providing the following information

Conversation: {conversation}
Information: {information}
"""}
  ]
)

print(completion.choices[0].message.content)

#for i in x:
#    print(str(i) + "\n")
