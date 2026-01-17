import { startTrip } from "../api/backend";

function StartTripButton() {
  const handleClick = async () => {
    const data = await startTrip({
      user_id: "user123",
      source: "College Gate",
      destination: "Metro Station",
    });

    console.log("Trip started:", data);
  };

  return <button onClick={handleClick}>Start Trip</button>;
}

export default StartTripButton;
