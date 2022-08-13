import 'package:english_words/english_words.dart';
import 'package:flutter/material.dart';
import 'package:inview_notifier_list/inview_notifier_list.dart';
import 'video_widget.dart';

void main() {
  runApp(const Etch());
}

class Etch extends StatelessWidget {
  const Etch({Key? key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    //final wordPair = WordPair.random();
    return MaterialApp(
      title: 'Fresh Plots',
      theme: ThemeData(
        primarySwatch: Colors.teal,
      ),
      home: Scaffold(
        appBar: AppBar(title: const Text("Fresh Plots")),
        body: VideoList(),
      ),
      debugShowCheckedModeBanner: false,
    );
  }
}
class VideoList extends StatelessWidget {
  final videos = ["big_buck_bunny_720p_1mb.mp4","sample-5s.mp4","sample-10s.m4", "sample-15s.mp4","SampleVideo_640x360_1mb.mp4",
    "SampleVideo_640x360_2mb.mp4","SampleVideo_720x480_1mb.mp4","SampleVideo_720x480_2mb.mp4","SampleVideo_1280x720_2mb.mp4"];
  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: <Widget>[
        InViewNotifierList(
          scrollDirection: Axis.vertical,
          initialInViewIds: ['0'],
          isInViewPortCondition:
              (double deltaTop, double deltaBottom, double viewPortDimension) {
            return deltaTop < (0.5 * viewPortDimension) &&
                deltaBottom > (0.5 * viewPortDimension);
          },
          itemCount: 9,
          builder: (BuildContext context, int index) {
            return
              Container(
                width: double.infinity,
                height: 300.0,
                alignment: Alignment.center,
                margin: EdgeInsets.symmetric(vertical: 50.0),
                child: LayoutBuilder(
                  builder: (BuildContext context, BoxConstraints constraints) {
                  return InViewNotifierWidget(
                    id: '$index',
                    builder:
                        (BuildContext context, bool isInView, Widget? child) {
                            var url = "http://127.0.0.1:5020/api/v2/video?content_id=${videos[index]}";
                            return VideoWidget(
                              play: isInView,
                              url:url);
                    },
                  );
                },
              ),

            );
          },
        ),
        Align(
          alignment: Alignment.center,
          child: Container(
            height: 1.0,

          ),
        )
      ],
    );
  }
}











class RandomWords extends StatefulWidget {
  const RandomWords({Key? key}) : super(key: key);

  @override
    State<RandomWords> createState() => _RandomWordsState();
}

class _RandomWordsState extends State<RandomWords> {
  final _suggestions = <WordPair>[];
  final _biggerFont = const TextStyle(fontSize: 18);
  final _savedSuggestions = <WordPair>{};
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title:const Text('Some title'),
          actions: [
            IconButton(onPressed: _savedSuggestionsView, icon: const Icon(Icons.list))
          ],

        ),
        body:ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemBuilder: (context, i){
        if (i.isOdd) return const Divider();

        final index = i ~/2;
        if (index >= _suggestions.length){
          _suggestions.addAll(generateWordPairs().take(10));
        }
        final alreadySaved = _savedSuggestions.contains(_suggestions[index]);
        return ListTile(
          title: Text(
            _suggestions[index].asPascalCase, style: _biggerFont,
          ),
          trailing: Icon(
            alreadySaved ? Icons.favorite : Icons.favorite_border,
            color: alreadySaved ? Colors.red : null,
            semanticLabel: alreadySaved ? 'Remove from saved' : 'Save',
          ),
          onTap: (){
            setState(() {
              if (alreadySaved){
                _savedSuggestions.remove(_suggestions[index]);
              }else{
                _savedSuggestions.add(_suggestions[index]);
              }
            });
          },
        );
      },
    ),
    );
    //return Text(wordPair.asPascalCase);
  }

  void _savedSuggestionsView(){
    Navigator.of(context).push(
        MaterialPageRoute<void>(
            builder: (context) {
              final tiles = _savedSuggestions.map(
                    (pair) {
                  return ListTile(
                    title: Text(pair.asPascalCase),
                  );
                },
              );
              final divided = tiles.isNotEmpty ?
              ListTile.divideTiles(
                context: context,
                tiles: tiles,
              ).toList()
                  : <Widget>[];

              return Scaffold(
                appBar: AppBar(
                  title: const Text('Saved Suggestions'),
                ),
                body: ListView(children: divided),
              );
            },
        ),
    );
  }
}
