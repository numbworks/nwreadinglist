```mermaid
classDiagram
  ComponentBag --* ReadingListProcessor : __component_bag
  RLAdapter --* ComponentBag : rl_adapter
  RLDataFrameFactory --* RLAdapter : __df_factory
  RLDataFrameHelper --* RLDataFrameFactory : __df_helper
  RLDataFrameHelper --* RSHighlighter : __df_helper
  RLReportManager --* ComponentBag : rlr_manager
  RSHighlighter --* RLAdapter : __rs_highlighter
  SettingBag --* ReadingListProcessor : __setting_bag
```
