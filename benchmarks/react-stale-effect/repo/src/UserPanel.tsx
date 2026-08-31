import { useEffect, useState } from "react";

type Props = {
  userId: string;
  fetchUser: (userId: string) => Promise<string>;
};

export function UserPanel({ userId, fetchUser }: Props) {
  const [name, setName] = useState("loading");

  useEffect(() => {
    let active = true;
    fetchUser(userId).then((nextName) => {
      if (active) setName(nextName);
    });
    return () => {
      active = false;
    };
  }, []);

  return <div>{name}</div>;
}
