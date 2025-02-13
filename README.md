# NBA Data Processing Project

## Overview
This project is a collection of scripts and modules dedicated to processing NBA data. It's still under construction due to the extensive nature of the work involved.

## Main Components

### Data_Getter2024
- **Main Script**: Contains the `DataGetter` Class.
- **Implementation**: Executed through `execute.py`.
- **Functionality**:
  - Collects game logs.
  - Creates team and player metadata in JSON format.
  - Calculates and appends metadata such as:
    - Average Offensive Box Plus/Minus (OBPM) of opponents guarding a player.
    - Height of the opponents guarding a player.
- **Data Sources**: 
  - Utilizes NBA API for play-by-play and matchup data.
  - Scrapes data from other relevant websites.

## Future Work
- Pull more data such as quarter by quarter data
- Process play by play and substitution info
- Create and implement ML models on the data
- Control System too perhaps
