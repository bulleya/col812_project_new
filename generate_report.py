import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set modern styling for the report
sns.set_theme(style="whitegrid", palette="muted")

def analyze_dram_trace(csv_file):
    print(f"Loading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # ---------------------------------------------------------
    # 1. CORE METRICS (Put these in your report text)
    # ---------------------------------------------------------
    counts = df['Command'].value_counts()
    rd = counts.get('RD', 0)
    wr = counts.get('WR', 0)
    act = counts.get('ACT', 0)
    pre = counts.get('PRE', 0)
    
    total_accesses = rd + wr
    rbhr = ((total_accesses - act) / total_accesses) * 100 if total_accesses > 0 else 0
    rw_ratio = rd / wr if wr > 0 else float('inf')
    
    print("\n" + "="*40)
    print(" 📊 METRICS FOR REPORT TEXT")
    print("="*40)
    print(f"Total Commands Logged: {len(df):,}")
    print(f"Row Buffer Hit Rate (RBHR): {rbhr:.2f}%")
    print(f"Read-to-Write Ratio: {rw_ratio:.2f} : 1")
    print(f"Total Activations (ACT): {act:,}")
    print(f"Total Precharges (PRE): {pre:,}")
    
    # ---------------------------------------------------------
    # GRAPH 1: Command Distribution Bar Chart
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=counts.index, y=counts.values, edgecolor=".2")
    plt.title("DRAM Command Distribution (Polybench 2D-Convolution)", fontsize=14, pad=15)
    plt.ylabel("Command Count (Millions)", fontsize=12)
    plt.xlabel("Command Type", fontsize=12)
    # Format y-axis to millions for readability
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}M".format(x/1e6)))
    plt.tight_layout()
    plt.savefig('fig1_command_distribution.png', dpi=300)
    
    # ---------------------------------------------------------
    # GRAPH 2: Memory Bandwidth / Traffic Over Time
    # ---------------------------------------------------------
    # Group by every 500 cycles to see traffic spikes
    cycle_bins = 500
    df['Cycle_Bin'] = (df['Cycle'] // cycle_bins) * cycle_bins
    time_series = df[df['Command'].isin(['RD', 'WR'])].groupby(['Cycle_Bin', 'Command']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(10, 5))
    plt.plot(time_series.index, time_series['RD'], label='Reads (RD)', color='#4C72B0', alpha=0.8)
    plt.plot(time_series.index, time_series['WR'], label='Writes (WR)', color='#C44E52', alpha=0.8)
    plt.title("DRAM Read/Write Traffic Over Time", fontsize=14, pad=15)
    plt.ylabel("Commands per 500 Cycles", fontsize=12)
    plt.xlabel("Simulation Cycle", fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig('fig2_traffic_over_time.png', dpi=300)

    # ---------------------------------------------------------
    # GRAPH 3: Partition Load Balancing (Heatmap)
    # ---------------------------------------------------------
    partition_cmd = df[df['Command'].isin(['RD', 'WR'])].groupby(['Partition', 'Command']).size().unstack(fill_value=0)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(partition_cmd, annot=True, fmt="d", cmap="YlGnBu", cbar_kws={'label': 'Command Count'})
    plt.title("Workload Distribution Across Memory Partitions", fontsize=14, pad=15)
    plt.ylabel("Memory Partition ID", fontsize=12)
    plt.xlabel("Command Type", fontsize=12)
    plt.tight_layout()
    plt.savefig('fig3_partition_heatmap.png', dpi=300)
    
    print("\n✅ Successfully generated 3 PNG graphs for your PDF report.")

if __name__ == "__main__":
    analyze_dram_trace("dram_trace.csv")
