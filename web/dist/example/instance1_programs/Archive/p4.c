void program4(dataframe* df) {
    group_by(df,0);
    count(df);
    arrange(df, ascending, 1);
    top_n(df,1,10);
}
