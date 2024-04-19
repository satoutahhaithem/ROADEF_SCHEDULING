for yearRodef in {2024..2021}; do
    source myenv/bin/activate
    # Define the session ranges for each year
    max_parallel_sessions_range_2024=($(seq 16 -1 9))
    max_parallel_sessions_range_2023=($(seq 18 -1 12))
    max_parallel_sessions_range_2022=($(seq 16 -1 11))
    max_parallel_sessions_range_2021=($(seq 10 -1 4))

    # Select the appropriate array based on the year
    case $yearRodef in
        2024)
            max_parallel_sessions_range=("${max_parallel_sessions_range_2024[@]}")
            ;;
        2023)
            max_parallel_sessions_range=("${max_parallel_sessions_range_2023[@]}")
            ;;
        2022)
            max_parallel_sessions_range=("${max_parallel_sessions_range_2022[@]}")
            ;;
        2021)
            max_parallel_sessions_range=("${max_parallel_sessions_range_2021[@]}")
            ;;
        *)
            echo "Year not supported"
            exit 1
    esac

    # Iterate over the selected array
    for max_par in "${max_parallel_sessions_range[@]}"; do
        python3 SchedulingInstSansZ.py ${yearRodef} ${max_par}
    done
done