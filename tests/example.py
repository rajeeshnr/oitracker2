"""
Example usage of the Option Chain Live Data Service.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.option_chain_service import OptionChainService
from src.services.data_storage_service import DataStorageService


async def example_basic_usage():
    """Basic example of using the Option Chain Service."""
    print("=== Basic Usage Example ===")
    
    # Initialize services
    option_service = OptionChainService()
    storage_service = DataStorageService()
    
    try:
        # Initialize the option chain service
        print("Initializing services...")
        await option_service.initialize()
        
        # Load option chain for NIFTY
        print("Loading NIFTY option chain...")
        await option_service.load_option_chain("NIFTY")
        
        # Get option chain summary
        summary = option_service.get_option_chain_summary()
        print(f"Loaded {summary['total_instruments']} instruments")
        
        # Get data for a specific strike
        strike_data = option_service.get_strike_data(18000)
        if "error" not in strike_data:
            print(f"Strike 18000 data: {strike_data}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await option_service.close()


async def example_live_streaming():
    """Example of live streaming with data storage."""
    print("\n=== Live Streaming Example ===")
    
    option_service = OptionChainService()
    storage_service = DataStorageService()
    
    try:
        # Initialize services
        await option_service.initialize()
        
        # Start live streaming
        print("Starting live streaming for NIFTY...")
        success = await option_service.start_live_streaming("NIFTY")
        
        if success:
            print("Live streaming started successfully!")
            
            # Monitor for 30 seconds
            for i in range(6):  # 6 * 5 seconds = 30 seconds
                await asyncio.sleep(5)
                
                # Get current summary
                summary = option_service.get_option_chain_summary()
                print(f"Update {i+1}: {summary['live_data_count']} instruments with live data")
                
                # Store data
                await storage_service.store_option_chain_data("NIFTY", summary)
            
            # Stop streaming
            await option_service.stop_live_streaming()
            print("Live streaming stopped")
            
        else:
            print("Failed to start live streaming")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await option_service.close()


async def example_data_analysis():
    """Example of analyzing option chain data."""
    print("\n=== Data Analysis Example ===")
    
    option_service = OptionChainService()
    
    try:
        await option_service.initialize()
        
        # Load option chain
        await option_service.load_option_chain("NIFTY")
        
        # Get summary
        summary = option_service.get_option_chain_summary()
        
        if "strike_summary" in summary:
            print("Analyzing strike data...")
            
            # Find strikes with highest OI
            max_oi_ce = 0
            max_oi_pe = 0
            max_oi_ce_strike = None
            max_oi_pe_strike = None
            
            for strike, data in summary["strike_summary"].items():
                ce_oi = data["CE"]["open_interest"]
                pe_oi = data["PE"]["open_interest"]
                
                if ce_oi > max_oi_ce:
                    max_oi_ce = ce_oi
                    max_oi_ce_strike = strike
                
                if pe_oi > max_oi_pe:
                    max_oi_pe = pe_oi
                    max_oi_pe_strike = strike
            
            print(f"Highest CE OI: {max_oi_ce} at strike {max_oi_ce_strike}")
            print(f"Highest PE OI: {max_oi_pe} at strike {max_oi_pe_strike}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await option_service.close()


async def main():
    """Run all examples."""
    print("Option Chain Live Data Service - Examples")
    print("=" * 50)
    
    # Run examples
    await example_basic_usage()
    await example_live_streaming()
    await example_data_analysis()
    
    print("\nExamples completed!")


if __name__ == "__main__":
    asyncio.run(main())
