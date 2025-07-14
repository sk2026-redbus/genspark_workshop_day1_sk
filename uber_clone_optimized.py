"""
Uber SK Console Application - OPTIMIZED VERSION
A high-performance cab booking system with three cab types: Uber Go, Uber Sedan, and Uber XL
Follows SOLID principles with performance optimizations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from functools import lru_cache
import time


class CabType(Enum):
    """Enum for different cab types with pricing configuration"""
    UBER_GO = ("Uber Go", 50.0, 12.0)
    UBER_SEDAN = ("Uber Sedan", 80.0, 18.0)
    UBER_XL = ("Uber XL", 120.0, 25.0)
    
    def __init__(self, display_name: str, base_fare: float, per_km_rate: float):
        self.display_name = display_name
        self.base_fare = base_fare
        self.per_km_rate = per_km_rate


class SurchargeType(Enum):
    """Enum for different surcharge types"""
    RUSH_HOUR = ("rush", 0.15, "per_km", "⏰ Prices increased due to peak hours")
    MIDNIGHT = ("midnight", 0.15, "base_fare", "🌙 Prices increased due to late night travel")
    OUTSTATION = ("outstation", 0.14, "per_km", "🛣️ Prices increased due to outstation location")
    
    def __init__(self, code: str, multiplier: float, applies_to: str, message: str):
        self.code = code
        self.multiplier = multiplier
        self.applies_to = applies_to
        self.message = message


class PricingConstants:
    """Centralized pricing constants for better maintainability"""
    OUTSTATION_THRESHOLD = 200.0
    RUSH_HOURS = frozenset([(8, 9), (17, 18)])  # Using frozenset for O(1) lookup
    MIDNIGHT_HOURS = frozenset(range(23, 24)) | frozenset(range(0, 5))  # 23-4


@dataclass(frozen=True)  # Immutable for better performance
class BookingRequest:
    """Immutable data class to encapsulate booking request information"""
    username: str
    destination: str
    distance_km: float
    booking_time: str  # Format: HH:MM
    
    def __post_init__(self):
        if self.distance_km <= 0:
            raise ValueError("Distance must be positive")
        if not self.username.strip():
            raise ValueError("Username cannot be empty")
        if not self.destination.strip():
            raise ValueError("Destination cannot be empty")
        self._validate_time_format()
    
    def _validate_time_format(self):
        """Optimized time validation"""
        try:
            hour, minute = map(int, self.booking_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time range")
        except (ValueError, TypeError):
            raise ValueError("Time must be in HH:MM format")
    
    @property
    @lru_cache(maxsize=1)  # Cache the hour extraction
    def hour(self) -> int:
        """Cached hour extraction"""
        return int(self.booking_time.split(':')[0])


@dataclass(frozen=True)  # Immutable for performance
class CabOption:
    """Immutable data class to represent a cab option with pricing"""
    cab_type: CabType
    price: float
    
    def __str__(self):
        return f"{self.cab_type.display_name}: ₹{self.price:.2f}"


class OptimizedPricingEngine:
    """High-performance pricing engine with caching and optimization"""
    
    def __init__(self):
        # Pre-compute surcharge conditions for faster lookup
        self._surcharge_conditions = self._build_surcharge_lookup()
    
    def _build_surcharge_lookup(self) -> Dict[str, callable]:
        """Pre-build surcharge condition functions"""
        return {
            'rush': lambda h, d: any(h in range(start, end + 1) for start, end in PricingConstants.RUSH_HOURS),
            'midnight': lambda h, d: h in PricingConstants.MIDNIGHT_HOURS,
            'outstation': lambda h, d: d > PricingConstants.OUTSTATION_THRESHOLD
        }
    
    @lru_cache(maxsize=128)  # Cache frequent calculations
    def calculate_price(self, cab_type: CabType, distance_km: float, hour: int) -> float:
        """Optimized price calculation with caching"""
        base_fare = cab_type.base_fare
        per_km_rate = cab_type.per_km_rate
        
        # Apply surcharges using optimized lookup
        for surcharge in SurchargeType:
            if self._surcharge_conditions[surcharge.code](hour, distance_km):
                if surcharge.applies_to == "base_fare":
                    base_fare *= (1 + surcharge.multiplier)
                else:  # per_km
                    per_km_rate *= (1 + surcharge.multiplier)
        
        return base_fare + (distance_km * per_km_rate)
    
    def get_all_options(self, distance_km: float, hour: int) -> List[CabOption]:
        """Get all cab options with optimized batch calculation"""
        return [
            CabOption(cab_type, self.calculate_price(cab_type, distance_km, hour))
            for cab_type in CabType
        ]
    
    @lru_cache(maxsize=64)
    def get_surcharge_messages(self, distance_km: float, hour: int) -> Tuple[str, ...]:
        """Cached surcharge message generation"""
        messages = []
        for surcharge in SurchargeType:
            if self._surcharge_conditions[surcharge.code](hour, distance_km):
                messages.append(surcharge.message)
        return tuple(messages)  # Return tuple for immutability and caching


class FastInputValidator:
    """Optimized input validator with minimal overhead"""
    
    @staticmethod
    def validate_non_empty(value: str) -> bool:
        """Fast non-empty validation"""
        return bool(value.strip())
    
    @staticmethod
    def validate_distance(distance: str) -> float:
        """Optimized distance validation"""
        try:
            dist = float(distance)
            if dist <= 0:
                raise ValueError("Distance must be positive")
            return dist
        except ValueError:
            raise ValueError("Invalid distance format")
    
    @staticmethod
    def validate_time(time_str: str) -> str:
        """Optimized time validation"""
        try:
            hour, minute = map(int, time_str.strip().split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Hour must be 0-23, minute must be 0-59")
            return f"{hour:02d}:{minute:02d}"
        except (ValueError, TypeError):
            raise ValueError("Time must be in HH:MM format")


class OptimizedDisplayFormatter:
    """Optimized display formatter with pre-built strings"""
    
    WELCOME_MESSAGE = """
╔══════════════════════════════════════╗
║           Welcome to Uber SK         ║
║     Your Ride, Your Choice, Your    ║
║            Destination!              ║
╚══════════════════════════════════════╝
"""
    
    @staticmethod
    def format_cab_options(options: List[CabOption]) -> str:
        """Optimized cab options formatting using join"""
        header = "\n🚗 Available Cab Options:\n" + "═" * 40 + "\n"
        options_str = "\n".join(f"{i}. {option}" for i, option in enumerate(options, 1))
        footer = "\n" + "═" * 40
        return header + options_str + footer
    
    @staticmethod
    def format_booking_summary(request: BookingRequest) -> str:
        """Optimized booking summary with f-string formatting"""
        return (f"\n📋 Booking Summary for {request.username}:\n"
                f"{'═' * 50}\n"
                f"📍 Destination: {request.destination}\n"
                f"📏 Distance: {request.distance_km} km\n"
                f"🕐 Booking Time: {request.booking_time}\n")
    
    @staticmethod
    def format_surcharge_messages(messages: Tuple[str, ...]) -> str:
        """Optimized surcharge message formatting"""
        return "\n" + "\n".join(messages) + "\n" if messages else ""


class UberSKOptimizedApp:
    """Optimized main application class with reduced overhead"""
    
    def __init__(self):
        self.pricing_engine = OptimizedPricingEngine()
        self.validator = FastInputValidator()
        self.formatter = OptimizedDisplayFormatter()
    
    def _get_validated_input(self, prompt: str, validator_func) -> any:
        """Optimized input collection with reduced exception handling overhead"""
        while True:
            try:
                return validator_func(input(prompt).strip())
            except ValueError as e:
                print(f"❌ Error: {e}\nPlease try again.\n")
    
    def _collect_booking_details(self) -> BookingRequest:
        """Optimized booking details collection"""
        print("Please provide your booking details:")
        print("-" * 40)
        
        # Use lambda functions for inline validation
        username = self._get_validated_input(
            "👤 Enter your username: ",
            lambda x: x if self.validator.validate_non_empty(x) else (_ for _ in ()).throw(ValueError("Username cannot be empty"))
        )
        
        destination = self._get_validated_input(
            "📍 Enter destination: ",
            lambda x: x if self.validator.validate_non_empty(x) else (_ for _ in ()).throw(ValueError("Destination cannot be empty"))
        )
        
        distance = self._get_validated_input(
            "📏 Enter distance in kilometers: ",
            self.validator.validate_distance
        )
        
        time_str = self._get_validated_input(
            "🕐 Enter booking time (HH:MM format, 24-hour): ",
            self.validator.validate_time
        )
        
        return BookingRequest(username, destination, distance, time_str)
    
    def _get_cab_choice(self, options: List[CabOption]) -> CabOption:
        """Optimized cab selection with minimal overhead"""
        print(self.formatter.format_cab_options(options))
        
        while True:
            try:
                choice_index = int(input("\n🚕 Choose your cab (1-3): ").strip()) - 1
                if 0 <= choice_index < len(options):
                    return options[choice_index]
                print("❌ Invalid choice. Please select 1, 2, or 3.")
            except ValueError:
                print("❌ Invalid input. Please enter a number (1-3).")
    
    def _confirm_booking(self, request: BookingRequest, selected_option: CabOption) -> bool:
        """Optimized booking confirmation"""
        print(f"\n🎯 You selected: {selected_option}")
        print(f"📋 Trip Summary:")
        print(f"   👤 Passenger: {request.username}")
        print(f"   📍 To: {request.destination}")
        print(f"   📏 Distance: {request.distance_km} km")
        print(f"   🕐 Time: {request.booking_time}")
        
        # Get surcharge messages efficiently
        surcharge_messages = self.pricing_engine.get_surcharge_messages(
            request.distance_km, request.hour
        )
        
        if surcharge_messages:
            for message in surcharge_messages:
                print(f"   {message}")
        else:
            print(f"   ✅ Standard pricing applied")
        
        print(f"   💰 Total Fare: ₹{selected_option.price:.2f}")
        
        while True:
            confirm = input("\n✅ Confirm booking? (y/n): ").strip().lower()
            if confirm in ('y', 'yes'):
                return True
            elif confirm in ('n', 'no'):
                return False
            print("❌ Please enter 'y' for yes or 'n' for no.")
    
    def run(self):
        """Optimized main application loop"""
        try:
            print(self.formatter.WELCOME_MESSAGE)
            
            # Collect booking details
            booking_request = self._collect_booking_details()
            
            # Calculate prices for all cab types
            cab_options = self.pricing_engine.get_all_options(
                booking_request.distance_km, 
                booking_request.hour
            )
            
            # Display booking summary
            print(self.formatter.format_booking_summary(booking_request))
            
            # Display surcharge messages if any
            surcharge_messages = self.pricing_engine.get_surcharge_messages(
                booking_request.distance_km, 
                booking_request.hour
            )
            
            if surcharge_messages:
                print(self.formatter.format_surcharge_messages(surcharge_messages))
            
            # Get user's cab choice
            selected_option = self._get_cab_choice(cab_options)
            
            # Confirm booking
            if self._confirm_booking(booking_request, selected_option):
                print("\n🎉 Booking Confirmed!")
                print("🚗 Your cab will arrive shortly.")
                print("📱 You will receive SMS updates about your ride.")
                print("\n👋 Thank you for choosing Uber SK!")
            else:
                print("\n❌ Booking cancelled.")
                print("👋 Thank you for visiting Uber SK!")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thank you for using Uber SK!")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
            print("👋 Thank you for using Uber SK!")


def main():
    """Optimized application entry point"""
    app = UberSKOptimizedApp()
    app.run()


if __name__ == "__main__":
    main()
