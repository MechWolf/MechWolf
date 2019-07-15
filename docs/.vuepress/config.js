module.exports = {
  title: "MechWolf",
  description: "Continuous flow process automation made easy",
  themeConfig: {
    logo: "/head10x.png",
    lastUpdated: "Last Updated", // string | boolean
    repo: "Benjamin-Lee/mechwolf",
    editLinks: true,
    nav: [
      { text: "Learn", link: "/about/intro/" },
      {
        text: "API Reference",
        items: [
          { text: "Overview", link: "/api/overview" },
          {
            text: "Modules",
            items: [
              { text: "core", link: "/api/core/" },
              {
                text: "stdlib",
                link: "/api/components/stdlib/"
              },
              {
                text: "contrib",
                link: "/api/components/contrib/"
              }
            ]
          }
        ]
      },
      {
        text: "Get Help",
        link: "https://github.com/Benjamin-Lee/MechWolf/issues/new/choose"
      }
    ],
    sidebar: {
      "/api/": [
        {
          title: "Core",
          collapsable: false,
          children: [
            "/api/core/apparatus",
            "/api/core/protocol",
            "/api/core/experiment"
          ]
        },
        {
          title: "Component Standard Library",
          collapsable: false,
          children: [
            "/api/components/stdlib/active_component.md",
            "/api/components/stdlib/broken_dummy_component.md",
            "/api/components/stdlib/component.md",
            "/api/components/stdlib/cross_mixer.md",
            "/api/components/stdlib/dummy.md",
            "/api/components/stdlib/dummy_pump.md",
            "/api/components/stdlib/dummy_sensor.md",
            "/api/components/stdlib/dummy_valve.md",
            "/api/components/stdlib/mixer.md",
            "/api/components/stdlib/pump.md",
            "/api/components/stdlib/sensor.md",
            "/api/components/stdlib/t_mixer.md",
            "/api/components/stdlib/tempcontrol.md",
            "/api/components/stdlib/tube.md",
            "/api/components/stdlib/valve.md",
            "/api/components/stdlib/vessel.md",
            "/api/components/stdlib/y_mixer.md"
          ]
        },
        {
          title: "Contributed Component Library",
          collapsable: false,
          children: [
            "/api/components/contrib/arduino.md",
            "/api/components/contrib/fc203.md",
            "/api/components/contrib/gsioc.md",
            "/api/components/contrib/labjack.md",
            "/api/components/contrib/varian.md",
            "/api/components/contrib/vici.md",
            "/api/components/contrib/vicipump.md"
          ]
        }
      ],
      "/": [
        {
          title: "About",
          collapsable: false,
          children: [
            "/about/intro",
            "/about/faq",
            "/about/support",
            "/about/why",
            "about/license"
          ]
        },
        {
          title: "Guide",
          collapsable: false,
          children: [
            "/guide/gentle_intro",
            "/guide/installation",
            "/guide/getting_started",
            "/guide/new_components"
          ]
        }
      ]
    }
  }
}
