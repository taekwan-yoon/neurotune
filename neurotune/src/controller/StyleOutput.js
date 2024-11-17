import React from "react";
import { Smile, Meh, Frown } from "lucide-react";
import "./OutputGraph.css";

const EmotionBars = ({ msg }) => {
  var neutral = 0;
  var positive = 0;
  var negative = 0;
  console.log(msg);
  if (msg && msg.length > 0) {
    const item = msg[0];
    const prediction = item.prediction; // "good", "neutral", or "bad"
    neutral = item.neutral.toFixed(3);
    positive = item.good.toFixed(3);
    negative = item.bad.toFixed(3);
  }

  const emotions = [
    {
      name: "Liked",
      value: positive,
      Icon: Smile,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500",
      gradient: "from-emerald-500",
      hoverBg: "hover:bg-gray-100",
    },
    {
      name: "Neutral",
      value: neutral,
      Icon: Meh,
      color: "text-amber-500",
      bgColor: "bg-amber-500",
      gradient: "from-amber-500",
      hoverBg: "hover:bg-gray-100",
    },
    {
      name: "Not Liked",
      value: negative,
      Icon: Frown,
      color: "text-rose-500",
      bgColor: "bg-rose-500",
      gradient: "from-rose-500",
      hoverBg: "hover:bg-gray-100",
    },
  ];

  // Find the highest probability
  const maxValue = Math.max(positive, neutral, negative);

  return (
    <div className="w-full max-w-md mx-auto p-8 space-y-6 bg-white rounded-xl shadow-lg">
      <div className="relative p-6 bg-gray-50 rounded-xl">
        <div className="flex justify-between items-end h-64 space-x-8">
          {emotions.map((emotion) => {
            const isHighest = emotion.value === maxValue;

            return (
              <div
                key={emotion.name}
                className="flex flex-col items-center space-y-6 flex-1"
              >
                <div
                  className={`
                    flex flex-col items-center p-3 rounded-xl
                    transition-all duration-300
                    ${
                      isHighest
                        ? `${emotion.bgColor} text-white shadow-lg scale-110`
                        : "text-gray-400 hover:bg-gray-100"
                    }
                  `}
                >
                  <emotion.Icon
                    className={`w-6 h-6 ${
                      !isHighest && "transition-transform hover:scale-110"
                    }`}
                  />
                  <span className="text-sm mt-1 font-medium">
                    {emotion.name}
                  </span>
                </div>

                <div className="relative w-full h-44">
                  <div className="absolute inset-0 bg-gray-200 rounded-xl overflow-hidden">
                    <div
                      className={`
                        absolute bottom-0 w-full transition-all duration-500 ease-out
                        ${emotion.bgColor} ${
                        isHighest ? "opacity-100" : "opacity-60"
                      }
                      `}
                      style={{
                        height: `${emotion.value * 100}%`,
                        boxShadow: isHighest
                          ? "inset 0 2px 4px rgba(0,0,0,0.1)"
                          : "none",
                      }}
                    >
                      {isHighest && (
                        <div className="w-full h-full animate-pulse opacity-20" />
                      )}
                    </div>
                  </div>
                </div>

                <div
                  className={`
                  font-mono text-sm font-medium
                  ${isHighest ? emotion.color : "text-gray-400"}
                `}
                >
                  {(emotion.value * 100).toFixed(0)}%
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default EmotionBars;
