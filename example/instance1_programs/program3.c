void program3(dataframe* df) {
    filter(df,ne,0,8);
    group_by(df,0);
    count(df);
    top_n(df,1,10);
}
