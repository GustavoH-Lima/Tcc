tempo=$(./mult m1 m2 6)
echo "$tempo"
novo_tempo="${tempo//./,}"
echo "$novo_tempo"

echo "mat_dim,versao,exec1,exec2,exec3,exec4,exec5" > "$arquivo_saida"
