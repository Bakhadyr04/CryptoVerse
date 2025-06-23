import React, { useEffect, useState } from "react";

export default function RecentUsersMarquee() {
  const [emails, setEmails] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("http://localhost:8000/recent-users/");
      const data = await response.json();
      setEmails(data.emails);
    };
    fetchData();
  }, []);

  const obfuscateEmail = (email: string): string => {
    const [local, domain] = email.split("@");
    if (local.length <= 3) return email;
    const visible = local.slice(0, local.length - 3);
    return `${visible}***@${domain}`;
};


  return (
    <div className="relative w-full h-[35px] pt-1 overflow-hidden bg-gradient-to-r bg-yellow-300">
      {/* Левые и правые маски */}
        <div className="absolute top-0 left-0 pl-10 pt-1 w-[400px] text-lg font-semibold text-black flex items-center  bg-yellow-300 z-10">
        Последние зарегистрированные пользователи:
        </div>
      {/* <div className="absolute top-0 right-0 w-16 h-full bg-yellow-300 z-10"></div>/ */}

      <div className="absolute whitespace-nowrap animate-marquee text-lg font-semibold text-black flex items-center h-full">
        {emails.map((email, index) => (
          <span key={index} className="mx-8">
            {obfuscateEmail(email)}
          </span>
        ))}
      </div>
    </div>
  );
}
