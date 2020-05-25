void program5(dataframe* df) {
    filter(df,ne,0,-1);
    group_by(df,0);
    count(df);
    arrange(df, ascending, 1);
    top_n(df,1,10);
}
