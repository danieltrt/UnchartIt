df1 <- df %>% group_by(col1)
df2 <- df1 %>% count()
df3 <- df2 %>% arrange(n)