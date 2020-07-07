void program2(dataframe* df) {
    group_by(df,0);
    count(df);
    arrange(df,descending,1);
}