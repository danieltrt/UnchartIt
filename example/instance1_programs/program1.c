void program1(dataframe* df) {
    group_by(df,0);
    count(df);
    top_n(df,1,10);
}
