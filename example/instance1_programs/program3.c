void program3(dataframe* df) {
    filter(df,ne,0,0);
    group_by(df,0);
    count(df);
    top_n(df,1,10);
}
