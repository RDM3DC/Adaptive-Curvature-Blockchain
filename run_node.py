from src.node import Node

def main():
    node = Node()


    import time
    for i in range(5):
        curvature = node.perform_optimization(problem_complexity=10)
        node.create_block(data=f"Block {i+1} | Curvature: {curvature:.4f}")
        time.sleep(0.5)  # 0.5-second delay for realistic timestamps

    # Print blockchain information
    for block in node.blockchain.chain:
        print(f"Index: {block.index}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Data: {block.data}")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}\n")

if __name__ == "__main__":
    main()
