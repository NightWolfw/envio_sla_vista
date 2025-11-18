import pathlib 
text=pathlib.Path('frontend/components/GroupsPageClient.tsx').read_text() 
print(text[:1000]) 
