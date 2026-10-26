# Выполнять после python3 setup_env.py и docker compose up -d --build --wait
# TOKEN — токен anna из POST /api/auth/token/. CAT_ID — id из ответа POST.
# Пароль и токен задаются локально и не включены в этот файл.
BASE=http://127.0.0.1:8000
curl -i "$BASE/api/achievements/"
curl -i -H "Authorization: Token $TOKEN" "$BASE/api/users/me/"
curl -i -X POST "$BASE/api/cats/" -H "Authorization: Token $TOKEN" -H 'Content-Type: application/json' --data '{"name":"Мурка","color":"orange","birth_year":2022,"achievements":[1]}'
curl -i -H "Authorization: Token $TOKEN" "$BASE/api/cats/$CAT_ID/"
curl -i -X PATCH "$BASE/api/cats/$CAT_ID/" -H "Authorization: Token $TOKEN" -H 'Content-Type: application/json' --data '{"color":"gray"}'
curl -i -X DELETE -H "Authorization: Token $TOKEN" "$BASE/api/cats/$CAT_ID/"
